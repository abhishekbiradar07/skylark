"""
Financial analytics - deterministic calculations
"""

from typing import List, Dict, Any, Optional
from decimal import Decimal
from data.models import WorkOrder, FinancialMetrics
import logging

logger = logging.getLogger(__name__)


def calculate_financial_metrics(
    work_orders: List[WorkOrder],
    sector_filter: Optional[str] = None
) -> FinancialMetrics:
    """
    Calculate financial metrics with deterministic Python logic
    
    Args:
        work_orders: List of normalized work orders
        sector_filter: Optional sector to filter by
        
    Returns:
        FinancialMetrics with calculated values
    """
    # Filter work orders
    filtered_wos = work_orders
    if sector_filter:
        filtered_wos = [wo for wo in filtered_wos if wo.sector == sector_filter]
    
    total_work_orders = len(filtered_wos)
    
    # Calculate billed values
    billed_wos = [wo for wo in filtered_wos if wo.billed_value_excl_gst]
    total_billed = sum(wo.billed_value_excl_gst for wo in billed_wos)
    
    # Calculate collected amounts
    collected_wos = [wo for wo in filtered_wos if wo.collected_amount]
    total_collected = sum(wo.collected_amount for wo in collected_wos)
    
    # Calculate receivables
    receivable_wos = [wo for wo in filtered_wos if wo.amount_receivable]
    total_receivable = sum(wo.amount_receivable for wo in receivable_wos)
    
    # Collection rate (collected / billed)
    # Note: collected is incl GST, billed is excl GST, so approximate
    collection_rate = None
    if total_billed > 0:
        # Rough approximation: assume 18% GST
        billed_with_gst = total_billed * Decimal("1.18")
        if billed_with_gst > 0:
            collection_rate = float(total_collected / billed_with_gst * 100)
    
    # By sector breakdown
    by_sector = {}
    sectors = set(wo.sector for wo in filtered_wos if wo.sector)
    for sector in sectors:
        sector_wos = [wo for wo in filtered_wos if wo.sector == sector]
        sector_billed_wos = [wo for wo in sector_wos if wo.billed_value_excl_gst]
        sector_collected_wos = [wo for wo in sector_wos if wo.collected_amount]
        sector_receivable_wos = [wo for wo in sector_wos if wo.amount_receivable]
        
        sector_billed = sum(wo.billed_value_excl_gst for wo in sector_billed_wos)
        sector_collected = sum(wo.collected_amount for wo in sector_collected_wos)
        sector_receivable = sum(wo.amount_receivable for wo in sector_receivable_wos)
        
        by_sector[sector] = {
            "work_orders": len(sector_wos),
            "billed": float(sector_billed),
            "collected": float(sector_collected),
            "receivable": float(sector_receivable)
        }
    
    # Data quality summary
    quality_summary = []
    
    missing_billed = total_work_orders - len(billed_wos)
    if missing_billed > 0:
        quality_summary.append(
            f"{missing_billed} work orders missing billed value"
        )
    
    missing_collected = total_work_orders - len(collected_wos)
    if missing_collected > 0:
        quality_summary.append(
            f"{missing_collected} work orders missing collected amount"
        )
    
    return FinancialMetrics(
        total_work_orders=total_work_orders,
        billed_work_orders=len(billed_wos),
        total_billed=total_billed,
        total_collected=total_collected,
        total_receivable=total_receivable,
        collection_rate=collection_rate,
        by_sector=by_sector,
        data_quality_summary=quality_summary
    )


def calculate_billed_value(work_orders: List[WorkOrder], **filters) -> Decimal:
    """Calculate total billed value"""
    metrics = calculate_financial_metrics(work_orders, **filters)
    return metrics.total_billed


def calculate_collected_amount(work_orders: List[WorkOrder], **filters) -> Decimal:
    """Calculate total collected amount"""
    metrics = calculate_financial_metrics(work_orders, **filters)
    return metrics.total_collected


def calculate_receivables(work_orders: List[WorkOrder], **filters) -> Decimal:
    """Calculate total receivables"""
    metrics = calculate_financial_metrics(work_orders, **filters)
    return metrics.total_receivable


def get_top_receivables(work_orders: List[WorkOrder], limit: int = 10) -> List[Dict[str, Any]]:
    """
    Get work orders with highest receivables
    
    Returns:
        List of WO dicts sorted by receivable descending
    """
    receivable_wos = [wo for wo in work_orders if wo.amount_receivable and wo.amount_receivable > 0]
    sorted_wos = sorted(receivable_wos, key=lambda wo: wo.amount_receivable, reverse=True)
    
    return [
        {
            "deal_name": wo.deal_name,
            "serial_number": wo.serial_number,
            "sector": wo.sector,
            "receivable": float(wo.amount_receivable),
            "billed": float(wo.billed_value_excl_gst) if wo.billed_value_excl_gst else 0,
            "collected": float(wo.collected_amount) if wo.collected_amount else 0
        }
        for wo in sorted_wos[:limit]
    ]
