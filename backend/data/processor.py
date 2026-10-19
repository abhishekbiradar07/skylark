"""
Process raw Monday.com data into normalized domain models
"""

from typing import List, Dict, Any
from .models import Deal, WorkOrder, DataQualityFlag
from .normalizer import (
    normalize_text, normalize_sector, normalize_status, normalize_probability,
    normalize_currency, normalize_date, is_header_fragment,
    normalize_execution_status, normalize_nature_of_work, normalize_stage
)
from .validator import validate_deal, validate_work_order
import logging

logger = logging.getLogger(__name__)


def process_deal(raw_deal: Dict[str, Any]) -> Deal:
    """
    Process a raw Monday.com deal into a normalized Deal model
    
    Args:
        raw_deal: Mapped deal dict from Monday API
        
    Returns:
        Normalized Deal instance
    """
    raw = raw_deal.get("raw", {})
    
    # Extract raw values
    raw_deal_name = raw.get("deal_name")
    raw_status = raw.get("deal_status")
    raw_sector = raw.get("sector")
    raw_probability = raw.get("closure_probability")
    raw_value = raw.get("deal_value")
    raw_stage = raw.get("deal_stage")
    
    # Normalize values
    deal_name = normalize_text(raw_deal_name)
    status = normalize_status(raw_status)
    sector = normalize_sector(raw_sector)
    probability_text, probability_numeric = normalize_probability(raw_probability)
    value = normalize_currency(raw_value)
    stage = normalize_stage(raw_stage)
    
    # Check for header fragments
    is_header = (
        is_header_fragment(raw_deal_name, "Deal Name") or
        is_header_fragment(raw_status, "Deal Status") or
        is_header_fragment(raw_stage, "Deal Stage")
    )
    
    # Parse dates
    close_date_actual = normalize_date(raw.get("close_date_actual"))
    tentative_close_date = normalize_date(raw.get("tentative_close_date"))
    created_date = normalize_date(raw.get("created_date"))
    
    # Create deal model
    deal = Deal(
        id=raw_deal.get("id"),
        raw_deal_name=raw_deal_name,
        raw_owner_code=raw.get("owner_code"),
        raw_client_code=raw.get("client_code"),
        raw_status=raw_status,
        raw_sector=raw_sector,
        raw_probability=raw_probability,
        raw_value=raw_value,
        raw_stage=raw_stage,
        deal_name=deal_name,
        owner_code=normalize_text(raw.get("owner_code")),
        client_code=normalize_text(raw.get("client_code")),
        status=status,
        sector=sector,
        probability=probability_text,
        probability_numeric=probability_numeric,
        value=value,
        stage=stage,
        product_deal=normalize_text(raw.get("product_deal")),
        close_date_actual=close_date_actual,
        tentative_close_date=tentative_close_date,
        created_date=created_date,
        is_header_fragment=is_header
    )
    
    # Validate and collect quality flags
    is_valid, quality_flags = validate_deal(deal)
    deal.is_valid = is_valid
    deal.quality_flags = quality_flags
    
    return deal


def process_work_order(raw_wo: Dict[str, Any]) -> WorkOrder:
    """
    Process a raw Monday.com work order into a normalized WorkOrder model
    
    Args:
        raw_wo: Mapped work order dict from Monday API
        
    Returns:
        Normalized WorkOrder instance
    """
    raw = raw_wo.get("raw", {})
    
    # Extract raw values
    raw_deal_name = raw.get("deal_name")
    raw_serial = raw.get("serial_number")
    raw_sector = raw.get("sector")
    raw_execution_status = raw.get("execution_status")
    raw_nature = raw.get("nature_of_work")
    
    # Normalize values
    deal_name = normalize_text(raw_deal_name)
    serial_number = normalize_text(raw_serial)
    sector = normalize_sector(raw_sector)
    execution_status = normalize_execution_status(raw_execution_status)
    nature_of_work = normalize_nature_of_work(raw_nature)
    
    # Check for header fragments
    is_header = (
        is_header_fragment(raw_serial, "Serial #") or
        is_header_fragment(raw_execution_status, "Execution Status")
    )
    
    # Parse financial values
    billed_value_excl = normalize_currency(raw.get("billed_value_excl_gst"))
    billed_value_incl = normalize_currency(raw.get("billed_value_incl_gst"))
    collected_amount = normalize_currency(raw.get("collected_amount"))
    amount_receivable = normalize_currency(raw.get("amount_receivable"))
    to_be_billed = normalize_currency(raw.get("to_be_billed_excl_gst"))
    
    # Parse dates
    po_date = normalize_date(raw.get("po_date"))
    probable_start = normalize_date(raw.get("probable_start_date"))
    probable_end = normalize_date(raw.get("probable_end_date"))
    data_delivery = normalize_date(raw.get("data_delivery_date"))
    last_invoice = normalize_date(raw.get("last_invoice_date"))
    
    # Create work order model
    wo = WorkOrder(
        id=raw_wo.get("id"),
        raw_deal_name=raw_deal_name,
        raw_serial=raw_serial,
        raw_sector=raw_sector,
        raw_execution_status=raw_execution_status,
        raw_nature_of_work=raw_nature,
        deal_name=deal_name,
        serial_number=serial_number,
        sector=sector,
        execution_status=execution_status,
        nature_of_work=nature_of_work,
        customer_code=normalize_text(raw.get("customer_code")),
        personnel_code=normalize_text(raw.get("personnel_code")),
        type_of_work=normalize_text(raw.get("type_of_work")),
        document_type=normalize_text(raw.get("document_type")),
        billed_value_excl_gst=billed_value_excl,
        billed_value_incl_gst=billed_value_incl,
        collected_amount=collected_amount,
        amount_receivable=amount_receivable,
        to_be_billed=to_be_billed,
        po_date=po_date,
        probable_start_date=probable_start,
        probable_end_date=probable_end,
        data_delivery_date=data_delivery,
        last_invoice_date=last_invoice,
        quantity_by_ops=normalize_text(raw.get("quantity_by_ops")),
        quantity_as_per_po=normalize_text(raw.get("quantity_as_per_po")),
        balance_quantity=normalize_text(raw.get("balance_quantity")),
        billing_status=normalize_text(raw.get("billing_status")),
        collection_status=normalize_text(raw.get("collection_status")),
        is_header_fragment=is_header
    )
    
    # Validate and collect quality flags
    is_valid, quality_flags = validate_work_order(wo)
    wo.is_valid = is_valid
    wo.quality_flags = quality_flags
    
    return wo


def process_deals(raw_deals: List[Dict[str, Any]]) -> List[Deal]:
    """Process multiple raw deals"""
    deals = []
    for raw_deal in raw_deals:
        try:
            deal = process_deal(raw_deal)
            deals.append(deal)
        except Exception as e:
            logger.error(f"Failed to process deal {raw_deal.get('id')}: {e}")
    
    # Filter out invalid deals (header fragments)
    valid_deals = [d for d in deals if d.is_valid]
    logger.info(f"Processed {len(deals)} deals, {len(valid_deals)} valid")
    
    return valid_deals


def process_work_orders(raw_wos: List[Dict[str, Any]]) -> List[WorkOrder]:
    """Process multiple raw work orders"""
    work_orders = []
    for raw_wo in raw_wos:
        try:
            wo = process_work_order(raw_wo)
            work_orders.append(wo)
        except Exception as e:
            logger.error(f"Failed to process work order {raw_wo.get('id')}: {e}")
    
    # Filter out invalid work orders
    valid_wos = [wo for wo in work_orders if wo.is_valid]
    logger.info(f"Processed {len(work_orders)} work orders, {len(valid_wos)} valid")
    
    return valid_wos
