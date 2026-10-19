"""
Cross-board analysis at SECTOR level
DO NOT force unreliable deal-level joins
"""

from typing import List, Dict, Any
from decimal import Decimal
from data.models import Deal, WorkOrder, SectorAnalysis
from analytics.pipeline import calculate_pipeline
from analytics.finance import calculate_financial_metrics
from .operations import calculate_operations_metrics
import logging

logger = logging.getLogger(__name__)


def analyze_sector_performance(
    deals: List[Deal],
    work_orders: List[WorkOrder],
    sector: str
) -> SectorAnalysis:
    """
    Analyze a specific sector across both boards
    Uses SECTOR-LEVEL aggregation only (no deal-level joins)
    
    Args:
        deals: All deals
        work_orders: All work orders
        sector: Sector to analyze
        
    Returns:
        SectorAnalysis with pipeline and operations metrics
    """
    # Calculate pipeline metrics for this sector
    pipeline_metrics = calculate_pipeline(deals, sector_filter=sector)
    
    # Calculate financial metrics for this sector
    finance_metrics = calculate_financial_metrics(work_orders, sector_filter=sector)
    
    # Calculate operations metrics for this sector
    ops_metrics = calculate_operations_metrics(work_orders, sector_filter=sector)
    
    # Determine strength levels
    pipeline_strength = classify_pipeline_strength(
        pipeline_metrics.known_pipeline,
        pipeline_metrics.total_deals
    )
    
    execution_strength = classify_execution_strength(
        finance_metrics.total_billed,
        ops_metrics.completed_work_orders,
        ops_metrics.total_work_orders
    )
    
    # Data quality notes
    quality_notes = []
    quality_notes.extend(pipeline_metrics.data_quality_summary)
    quality_notes.extend(finance_metrics.data_quality_summary)
    quality_notes.append(
        f"Analysis is SECTOR-LEVEL only (no deal-to-WO join attempted)"
    )
    
    return SectorAnalysis(
        sector=sector,
        deals_count=pipeline_metrics.total_deals,
        pipeline_value=pipeline_metrics.known_pipeline,
        weighted_pipeline=pipeline_metrics.weighted_pipeline,
        work_orders_count=ops_metrics.total_work_orders,
        billed_value=finance_metrics.total_billed,
        collected_amount=finance_metrics.total_collected,
        active_projects=ops_metrics.active_work_orders,
        completed_projects=ops_metrics.completed_work_orders,
        pipeline_strength=pipeline_strength,
        execution_strength=execution_strength,
        data_quality_notes=quality_notes
    )


def compare_sectors(
    deals: List[Deal],
    work_orders: List[WorkOrder],
    sector1: str,
    sector2: str
) -> Dict[str, SectorAnalysis]:
    """
    Compare two sectors
    
    Returns:
        Dict with sector1 and sector2 as keys
    """
    analysis1 = analyze_sector_performance(deals, work_orders, sector1)
    analysis2 = analyze_sector_performance(deals, work_orders, sector2)
    
    return {
        sector1: analysis1,
        sector2: analysis2
    }


def analyze_all_sectors(
    deals: List[Deal],
    work_orders: List[WorkOrder]
) -> Dict[str, SectorAnalysis]:
    """
    Analyze all sectors
    
    Returns:
        Dict of sector name → SectorAnalysis
    """
    # Get unique sectors from both boards
    deal_sectors = set(d.sector for d in deals if d.sector)
    wo_sectors = set(wo.sector for wo in work_orders if wo.sector)
    all_sectors = deal_sectors.union(wo_sectors)
    
    analyses = {}
    for sector in all_sectors:
        try:
            analyses[sector] = analyze_sector_performance(deals, work_orders, sector)
        except Exception as e:
            logger.error(f"Failed to analyze sector {sector}: {e}")
    
    return analyses


def identify_pipeline_execution_gaps(
    deals: List[Deal],
    work_orders: List[WorkOrder]
) -> List[Dict[str, Any]]:
    """
    Identify sectors with strong pipeline but weak execution (or vice versa)
    
    Returns:
        List of gap analysis dicts
    """
    sector_analyses = analyze_all_sectors(deals, work_orders)
    
    gaps = []
    for sector, analysis in sector_analyses.items():
        # Strong pipeline, weak execution
        if analysis.pipeline_strength in ["High", "Medium"] and analysis.execution_strength == "Low":
            gaps.append({
                "sector": sector,
                "gap_type": "Strong pipeline, weak execution",
                "deals_count": analysis.deals_count,
                "pipeline_value": float(analysis.pipeline_value),
                "work_orders_count": analysis.work_orders_count,
                "billed_value": float(analysis.billed_value),
                "insight": f"{sector} has {analysis.pipeline_strength.lower()} pipeline but low execution"
            })
        
        # Weak pipeline, strong execution
        if analysis.pipeline_strength == "Low" and analysis.execution_strength in ["High", "Medium"]:
            gaps.append({
                "sector": sector,
                "gap_type": "Weak pipeline, strong execution",
                "deals_count": analysis.deals_count,
                "pipeline_value": float(analysis.pipeline_value),
                "work_orders_count": analysis.work_orders_count,
                "billed_value": float(analysis.billed_value),
                "insight": f"{sector} has strong execution but low pipeline (growth risk)"
            })
    
    return gaps


def classify_pipeline_strength(pipeline_value: Decimal, deal_count: int) -> str:
    """
    Classify pipeline strength
    
    Returns:
        "High", "Medium", or "Low"
    """
    # Based on actual data audit: total pipeline ~₹230 Cr across 346 deals
    # Average per deal: ~₹67L
    
    if deal_count == 0:
        return "Low"
    
    avg_deal_value = pipeline_value / deal_count
    
    # Thresholds (can be tuned)
    if pipeline_value > Decimal("50000000") and avg_deal_value > Decimal("1000000"):
        return "High"
    elif pipeline_value > Decimal("10000000"):
        return "Medium"
    else:
        return "Low"


def classify_execution_strength(
    billed_value: Decimal,
    completed_count: int,
    total_count: int
) -> str:
    """
    Classify execution strength
    
    Returns:
        "High", "Medium", or "Low"
    """
    if total_count == 0:
        return "Low"
    
    completion_rate = completed_count / total_count
    
    # Based on actual data audit: ~₹10.7 Cr billed, 117/176 completed
    if billed_value > Decimal("20000000") and completion_rate > 0.6:
        return "High"
    elif billed_value > Decimal("5000000") or completion_rate > 0.5:
        return "Medium"
    else:
        return "Low"
