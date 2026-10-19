"""
Data validation and quality checking
"""

from typing import List, Dict, Any
from .models import Deal, WorkOrder, DataQualityFlag
from datetime import datetime


def validate_deal(deal: Deal) -> tuple[bool, List[DataQualityFlag]]:
    """
    Validate a deal and return quality flags
    
    Returns:
        Tuple of (is_valid, quality_flags)
    """
    flags = []
    is_valid = True
    
    # Check for header fragments
    if deal.is_header_fragment:
        is_valid = False
        flags.append(DataQualityFlag(
            field="deal_name",
            issue="HEADER_FRAGMENT",
            severity="error"
        ))
    
    # Missing critical fields
    if not deal.deal_name:
        flags.append(DataQualityFlag(
            field="deal_name",
            issue="MISSING_DEAL_NAME",
            severity="warning"
        ))
    
    if not deal.sector:
        flags.append(DataQualityFlag(
            field="sector",
            issue="MISSING_SECTOR",
            severity="warning"
        ))
    
    if not deal.status:
        flags.append(DataQualityFlag(
            field="status",
            issue="MISSING_STATUS",
            severity="warning"
        ))
    
    # Missing financial value
    if not deal.value:
        flags.append(DataQualityFlag(
            field="value",
            issue="MISSING_DEAL_VALUE",
            severity="warning"
        ))
    
    # Missing probability
    if not deal.probability:
        flags.append(DataQualityFlag(
            field="probability",
            issue="MISSING_PROBABILITY",
            severity="info"
        ))
    
    # Date issues
    if not deal.tentative_close_date and deal.status == "Open":
        flags.append(DataQualityFlag(
            field="tentative_close_date",
            issue="MISSING_EXPECTED_CLOSE_DATE",
            severity="warning"
        ))
    
    return is_valid, flags


def validate_work_order(wo: WorkOrder) -> tuple[bool, List[DataQualityFlag]]:
    """
    Validate a work order and return quality flags
    
    Returns:
        Tuple of (is_valid, quality_flags)
    """
    flags = []
    is_valid = True
    
    # Check for header fragments
    if wo.is_header_fragment:
        is_valid = False
        flags.append(DataQualityFlag(
            field="serial_number",
            issue="HEADER_FRAGMENT",
            severity="error"
        ))
    
    # Missing critical fields
    if not wo.deal_name:
        flags.append(DataQualityFlag(
            field="deal_name",
            issue="MISSING_DEAL_NAME",
            severity="warning"
        ))
    
    if not wo.sector:
        flags.append(DataQualityFlag(
            field="sector",
            issue="MISSING_SECTOR",
            severity="error"
        ))
    
    if not wo.execution_status:
        flags.append(DataQualityFlag(
            field="execution_status",
            issue="MISSING_EXECUTION_STATUS",
            severity="warning"
        ))
    
    # Financial data quality
    if not wo.billed_value_excl_gst:
        flags.append(DataQualityFlag(
            field="billed_value",
            issue="MISSING_BILLED_VALUE",
            severity="warning"
        ))
    
    if not wo.collected_amount:
        flags.append(DataQualityFlag(
            field="collected_amount",
            issue="MISSING_COLLECTED_AMOUNT",
            severity="info"
        ))
    
    # Check for delayed projects
    if wo.execution_status == "Not Started" and wo.probable_start_date:
        if wo.probable_start_date < datetime.now():
            flags.append(DataQualityFlag(
                field="execution_status",
                issue="PROJECT_DELAYED",
                severity="warning"
            ))
    
    return is_valid, flags


def summarize_quality_issues(deals: List[Deal], work_orders: List[WorkOrder]) -> Dict[str, Any]:
    """
    Generate a summary of data quality issues across all records
    
    Returns:
        Dict with quality summary stats
    """
    summary = {
        "deals": {
            "total": len(deals),
            "valid": sum(1 for d in deals if d.is_valid),
            "missing_values": 0,
            "missing_probabilities": 0,
            "missing_close_dates": 0,
        },
        "work_orders": {
            "total": len(work_orders),
            "valid": sum(1 for wo in work_orders if wo.is_valid),
            "missing_billed": 0,
            "missing_collected": 0,
        },
        "critical_issues": [],
        "warnings": []
    }
    
    # Analyze deals
    for deal in deals:
        if not deal.value:
            summary["deals"]["missing_values"] += 1
        if not deal.probability:
            summary["deals"]["missing_probabilities"] += 1
        if not deal.tentative_close_date and deal.status == "Open":
            summary["deals"]["missing_close_dates"] += 1
    
    # Analyze work orders
    for wo in work_orders:
        if not wo.billed_value_excl_gst:
            summary["work_orders"]["missing_billed"] += 1
        if not wo.collected_amount:
            summary["work_orders"]["missing_collected"] += 1
    
    # Critical issues
    if summary["deals"]["missing_values"] > 0:
        pct = (summary["deals"]["missing_values"] / summary["deals"]["total"] * 100)
        summary["critical_issues"].append(
            f"{summary['deals']['missing_values']} deals ({pct:.1f}%) missing deal values"
        )
    
    if summary["work_orders"]["missing_billed"] > 0:
        pct = (summary["work_orders"]["missing_billed"] / summary["work_orders"]["total"] * 100)
        summary["warnings"].append(
            f"{summary['work_orders']['missing_billed']} work orders ({pct:.1f}%) missing billed values"
        )
    
    return summary
