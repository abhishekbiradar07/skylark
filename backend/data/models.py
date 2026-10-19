"""
Domain models for normalized business data
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field


class DataQualityFlag(BaseModel):
    """Data quality issue flag"""
    field: str
    issue: str
    severity: str = "warning"  # warning, error


class Deal(BaseModel):
    """Normalized deal model"""
    id: str
    
    # Raw values (preserved from Monday)
    raw_deal_name: Optional[str] = None
    raw_owner_code: Optional[str] = None
    raw_client_code: Optional[str] = None
    raw_status: Optional[str] = None
    raw_sector: Optional[str] = None
    raw_probability: Optional[str] = None
    raw_value: Optional[str] = None
    raw_stage: Optional[str] = None
    
    # Normalized values
    deal_name: Optional[str] = None
    owner_code: Optional[str] = None
    client_code: Optional[str] = None
    status: Optional[str] = None
    sector: Optional[str] = None
    probability: Optional[str] = None
    probability_numeric: Optional[float] = None
    value: Optional[Decimal] = None
    stage: Optional[str] = None
    product_deal: Optional[str] = None
    
    # Dates
    close_date_actual: Optional[datetime] = None
    tentative_close_date: Optional[datetime] = None
    created_date: Optional[datetime] = None
    
    # Data quality
    quality_flags: List[DataQualityFlag] = Field(default_factory=list)
    is_valid: bool = True
    is_header_fragment: bool = False


class WorkOrder(BaseModel):
    """Normalized work order model"""
    id: str
    
    # Raw values
    raw_deal_name: Optional[str] = None
    raw_serial: Optional[str] = None
    raw_sector: Optional[str] = None
    raw_execution_status: Optional[str] = None
    raw_nature_of_work: Optional[str] = None
    
    # Normalized values
    deal_name: Optional[str] = None
    serial_number: Optional[str] = None
    sector: Optional[str] = None
    execution_status: Optional[str] = None
    nature_of_work: Optional[str] = None
    customer_code: Optional[str] = None
    personnel_code: Optional[str] = None
    type_of_work: Optional[str] = None
    document_type: Optional[str] = None
    
    # Financial (all in INR)
    billed_value_excl_gst: Optional[Decimal] = None
    billed_value_incl_gst: Optional[Decimal] = None
    collected_amount: Optional[Decimal] = None
    amount_receivable: Optional[Decimal] = None
    to_be_billed: Optional[Decimal] = None
    
    # Dates
    po_date: Optional[datetime] = None
    probable_start_date: Optional[datetime] = None
    probable_end_date: Optional[datetime] = None
    data_delivery_date: Optional[datetime] = None
    last_invoice_date: Optional[datetime] = None
    
    # Quantities
    quantity_by_ops: Optional[str] = None
    quantity_as_per_po: Optional[str] = None
    quantity_billed: Optional[float] = None
    balance_quantity: Optional[str] = None
    
    # Status fields
    billing_status: Optional[str] = None
    collection_status: Optional[str] = None
    
    # Data quality
    quality_flags: List[DataQualityFlag] = Field(default_factory=list)
    is_valid: bool = True
    is_header_fragment: bool = False


class PipelineMetrics(BaseModel):
    """Pipeline analysis metrics"""
    total_deals: int
    valued_deals: int
    excluded_deals: int
    
    known_pipeline: Decimal
    weighted_pipeline: Decimal
    
    by_sector: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    by_stage: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    by_probability: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    
    data_quality_summary: List[str] = Field(default_factory=list)


class FinancialMetrics(BaseModel):
    """Financial performance metrics"""
    total_work_orders: int
    billed_work_orders: int
    
    total_billed: Decimal
    total_collected: Decimal
    total_receivable: Decimal
    collection_rate: Optional[float] = None
    
    by_sector: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    
    data_quality_summary: List[str] = Field(default_factory=list)


class OperationsMetrics(BaseModel):
    """Operations performance metrics"""
    total_work_orders: int
    active_work_orders: int
    completed_work_orders: int
    delayed_work_orders: int
    
    by_sector: Dict[str, int] = Field(default_factory=dict)
    by_status: Dict[str, int] = Field(default_factory=dict)
    
    delayed_projects: List[Dict[str, Any]] = Field(default_factory=list)
    
    data_quality_summary: List[str] = Field(default_factory=list)


class SectorAnalysis(BaseModel):
    """Cross-board sector analysis"""
    sector: str
    
    # Pipeline data
    deals_count: int
    pipeline_value: Decimal
    weighted_pipeline: Decimal
    
    # Operations data
    work_orders_count: int
    billed_value: Decimal
    collected_amount: Decimal
    active_projects: int
    completed_projects: int
    
    # Insights
    pipeline_strength: str  # High/Medium/Low
    execution_strength: str  # High/Medium/Low
    
    data_quality_notes: List[str] = Field(default_factory=list)


class DataQualityReport(BaseModel):
    """Comprehensive data quality report"""
    deals_total: int
    deals_valid: int
    deals_issues: List[Dict[str, Any]] = Field(default_factory=list)
    
    work_orders_total: int
    work_orders_valid: int
    work_orders_issues: List[Dict[str, Any]] = Field(default_factory=list)
    
    critical_issues: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
