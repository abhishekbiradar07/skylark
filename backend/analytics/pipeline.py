"""
Pipeline analytics - deterministic calculations
"""

from typing import List, Dict, Any, Optional
from decimal import Decimal
from datetime import datetime
from data.models import Deal, PipelineMetrics
import logging

logger = logging.getLogger(__name__)


def calculate_pipeline(
    deals: List[Deal],
    sector_filter: Optional[str] = None,
    status_filter: Optional[List[str]] = None,
    quarter: Optional[str] = None
) -> PipelineMetrics:
    """
    Calculate pipeline metrics with deterministic Python logic
    
    Args:
        deals: List of normalized deals
        sector_filter: Optional sector to filter by
        status_filter: Optional list of statuses (default: ["Open", "Won"])
        quarter: Optional quarter filter (e.g., "Q3 2026")
        
    Returns:
        PipelineMetrics with calculated values
    """
    if status_filter is None:
        status_filter = ["Open", "Won"]
    
    # Filter deals
    filtered_deals = deals
    
    if sector_filter:
        filtered_deals = [d for d in filtered_deals if d.sector == sector_filter]
    
    if status_filter:
        filtered_deals = [d for d in filtered_deals if d.status in status_filter]
    
    # Apply quarter filter if specified
    if quarter:
        start_date, end_date = parse_quarter(quarter)
        filtered_deals = [
            d for d in filtered_deals
            if d.tentative_close_date and start_date <= d.tentative_close_date <= end_date
        ]
    
    # Calculate metrics
    total_deals = len(filtered_deals)
    valued_deals = [d for d in filtered_deals if d.value and d.value > 0]
    excluded_deals = total_deals - len(valued_deals)
    
    # Known pipeline: Sum of non-null values
    known_pipeline = Decimal(0)
    for deal in valued_deals:
        known_pipeline += deal.value
    
    # Weighted pipeline: Sum of value * probability
    weighted_pipeline = Decimal(0)
    for deal in valued_deals:
        prob = deal.probability_numeric if deal.probability_numeric else 0.3  # Conservative default
        weighted_pipeline += deal.value * Decimal(str(prob))
    
    # By sector breakdown
    by_sector = {}
    sectors = set(d.sector for d in valued_deals if d.sector)
    for sector in sectors:
        sector_deals = [d for d in valued_deals if d.sector == sector]
        sector_known = sum(d.value for d in sector_deals)
        sector_weighted = sum(
            d.value * Decimal(str(d.probability_numeric if d.probability_numeric else 0.3))
            for d in sector_deals
        )
        by_sector[sector] = {
            "deals": len(sector_deals),
            "known_pipeline": float(sector_known),
            "weighted_pipeline": float(sector_weighted)
        }
    
    # By stage breakdown
    by_stage = {}
    stages = set(d.stage for d in valued_deals if d.stage)
    for stage in stages:
        stage_deals = [d for d in valued_deals if d.stage == stage]
        stage_known = sum(d.value for d in stage_deals)
        by_stage[stage] = {
            "deals": len(stage_deals),
            "known_pipeline": float(stage_known)
        }
    
    # By probability breakdown
    by_probability = {}
    probs = set(d.probability for d in valued_deals if d.probability)
    for prob in probs:
        prob_deals = [d for d in valued_deals if d.probability == prob]
        prob_known = sum(d.value for d in prob_deals)
        by_probability[prob] = {
            "deals": len(prob_deals),
            "known_pipeline": float(prob_known)
        }
    
    # Data quality summary
    quality_summary = []
    if excluded_deals > 0:
        quality_summary.append(
            f"{excluded_deals} deals excluded due to missing deal values"
        )
    
    missing_probs = sum(1 for d in valued_deals if not d.probability)
    if missing_probs > 0:
        quality_summary.append(
            f"{missing_probs} deals missing probability (using conservative 0.3 default)"
        )
    
    return PipelineMetrics(
        total_deals=total_deals,
        valued_deals=len(valued_deals),
        excluded_deals=excluded_deals,
        known_pipeline=known_pipeline,
        weighted_pipeline=weighted_pipeline,
        by_sector=by_sector,
        by_stage=by_stage,
        by_probability=by_probability,
        data_quality_summary=quality_summary
    )


def parse_quarter(quarter_str: str) -> tuple[datetime, datetime]:
    """
    Parse quarter string to date range
    
    Args:
        quarter_str: e.g., "Q3 2026", "Q1", "this quarter"
        
    Returns:
        Tuple of (start_date, end_date)
    """
    now = datetime.now()
    current_year = now.year
    
    # Handle "this quarter"
    if "this" in quarter_str.lower():
        current_month = now.month
        if current_month <= 3:
            q = 1
        elif current_month <= 6:
            q = 2
        elif current_month <= 9:
            q = 3
        else:
            q = 4
        year = current_year
    else:
        # Parse "Q3 2026" format
        parts = quarter_str.upper().replace("Q", "").strip().split()
        q = int(parts[0])
        year = int(parts[1]) if len(parts) > 1 else current_year
    
    # Calculate quarter date range
    if q == 1:
        start = datetime(year, 1, 1)
        end = datetime(year, 3, 31, 23, 59, 59)
    elif q == 2:
        start = datetime(year, 4, 1)
        end = datetime(year, 6, 30, 23, 59, 59)
    elif q == 3:
        start = datetime(year, 7, 1)
        end = datetime(year, 9, 30, 23, 59, 59)
    else:  # Q4
        start = datetime(year, 10, 1)
        end = datetime(year, 12, 31, 23, 59, 59)
    
    return start, end


def get_current_quarter() -> str:
    """Get current quarter string (e.g., 'Q3 2026')"""
    now = datetime.now()
    month = now.month
    
    if month <= 3:
        q = 1
    elif month <= 6:
        q = 2
    elif month <= 9:
        q = 3
    else:
        q = 4
    
    return f"Q{q} {now.year}"


def calculate_weighted_pipeline(deals: List[Deal], **filters) -> Decimal:
    """Calculate weighted pipeline with filters"""
    metrics = calculate_pipeline(deals, **filters)
    return metrics.weighted_pipeline


def calculate_sector_pipeline(deals: List[Deal]) -> Dict[str, Dict[str, Any]]:
    """Calculate pipeline broken down by sector"""
    metrics = calculate_pipeline(deals)
    return metrics.by_sector


def get_top_opportunities(deals: List[Deal], limit: int = 10) -> List[Dict[str, Any]]:
    """
    Get top opportunities by deal value
    
    Returns:
        List of deal dicts sorted by value descending
    """
    valued_deals = [d for d in deals if d.value and d.value > 0 and d.status == "Open"]
    sorted_deals = sorted(valued_deals, key=lambda d: d.value, reverse=True)
    
    return [
        {
            "deal_name": d.deal_name,
            "sector": d.sector,
            "value": float(d.value),
            "probability": d.probability,
            "stage": d.stage,
            "tentative_close_date": d.tentative_close_date.isoformat() if d.tentative_close_date else None
        }
        for d in sorted_deals[:limit]
    ]
