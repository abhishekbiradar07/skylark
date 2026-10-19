"""
Operations analytics - deterministic calculations
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from data.models import WorkOrder, OperationsMetrics
import logging

logger = logging.getLogger(__name__)


def calculate_operations_metrics(
    work_orders: List[WorkOrder],
    sector_filter: Optional[str] = None
) -> OperationsMetrics:
    """
    Calculate operations metrics with deterministic Python logic
    
    Args:
        work_orders: List of normalized work orders
        sector_filter: Optional sector to filter by
        
    Returns:
        OperationsMetrics with calculated values
    """
    # Filter work orders
    filtered_wos = work_orders
    if sector_filter:
        filtered_wos = [wo for wo in filtered_wos if wo.sector == sector_filter]
    
    total_work_orders = len(filtered_wos)
    
    # Active work orders (Ongoing, Not Started)
    active_statuses = ["Ongoing", "Not Started", "Executed until current month"]
    active_wos = [wo for wo in filtered_wos if wo.execution_status in active_statuses]
    active_count = len(active_wos)
    
    # Completed work orders
    completed_wos = [wo for wo in filtered_wos if wo.execution_status == "Completed"]
    completed_count = len(completed_wos)
    
    # Delayed work orders (Not Started but past probable start date, or Pause/Struck)
    delayed_wos = []
    now = datetime.now()
    for wo in filtered_wos:
        if wo.execution_status == "Pause / Struck":
            delayed_wos.append(wo)
        elif wo.execution_status == "Not Started" and wo.probable_start_date:
            if wo.probable_start_date < now:
                delayed_wos.append(wo)
    delayed_count = len(delayed_wos)
    
    # By sector breakdown
    by_sector = {}
    sectors = set(wo.sector for wo in filtered_wos if wo.sector)
    for sector in sectors:
        sector_wos = [wo for wo in filtered_wos if wo.sector == sector]
        by_sector[sector] = len(sector_wos)
    
    # By status breakdown
    by_status = {}
    statuses = set(wo.execution_status for wo in filtered_wos if wo.execution_status)
    for status in statuses:
        status_wos = [wo for wo in filtered_wos if wo.execution_status == status]
        by_status[status] = len(status_wos)
    
    # Delayed projects details
    delayed_projects = [
        {
            "deal_name": wo.deal_name,
            "serial_number": wo.serial_number,
            "sector": wo.sector,
            "execution_status": wo.execution_status,
            "probable_start_date": wo.probable_start_date.isoformat() if wo.probable_start_date else None,
            "probable_end_date": wo.probable_end_date.isoformat() if wo.probable_end_date else None
        }
        for wo in delayed_wos
    ]
    
    # Data quality summary
    quality_summary = []
    missing_status = sum(1 for wo in filtered_wos if not wo.execution_status)
    if missing_status > 0:
        quality_summary.append(
            f"{missing_status} work orders missing execution status"
        )
    
    return OperationsMetrics(
        total_work_orders=total_work_orders,
        active_work_orders=active_count,
        completed_work_orders=completed_count,
        delayed_work_orders=delayed_count,
        by_sector=by_sector,
        by_status=by_status,
        delayed_projects=delayed_projects,
        data_quality_summary=quality_summary
    )


def get_delayed_work_orders(work_orders: List[WorkOrder]) -> List[WorkOrder]:
    """Get list of delayed work orders"""
    metrics = calculate_operations_metrics(work_orders)
    # Return full WO objects for delayed projects
    delayed_wos = []
    now = datetime.now()
    for wo in work_orders:
        if wo.execution_status == "Pause / Struck":
            delayed_wos.append(wo)
        elif wo.execution_status == "Not Started" and wo.probable_start_date:
            if wo.probable_start_date < now:
                delayed_wos.append(wo)
    return delayed_wos
