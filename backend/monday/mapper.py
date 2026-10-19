"""
Maps raw Monday.com API responses to domain models
"""

from typing import Dict, Any, Optional, List
import json


def extract_column_value(column_values: List[Dict[str, Any]], column_title: str) -> Optional[str]:
    """
    Extract a column value by title from Monday.com column_values array
    
    Args:
        column_values: List of column value dicts from Monday API
        column_title: Column title to search for
        
    Returns:
        Text value or None
    """
    for col in column_values:
        if col.get("title") == column_title:
            return col.get("text")
    return None


def extract_column_value_json(column_values: List[Dict[str, Any]], column_title: str) -> Optional[Any]:
    """
    Extract and parse JSON column value
    
    Args:
        column_values: List of column value dicts
        column_title: Column title to search for
        
    Returns:
        Parsed JSON value or None
    """
    for col in column_values:
        if col.get("title") == column_title:
            value_str = col.get("value")
            if value_str:
                try:
                    return json.loads(value_str)
                except:
                    return None
    return None


def map_deal_item(item: Dict[str, Any]) -> Dict[str, Any]:
    """
    Map a raw Monday.com deal item to structured format
    
    Args:
        item: Raw item from Monday API
        
    Returns:
        Structured deal dict with raw values preserved
    """
    column_values = item.get("column_values", [])
    
    return {
        "id": item.get("id"),
        "item_name": item.get("name"),
        "raw": {
            "deal_name": extract_column_value(column_values, "Deal Name"),
            "owner_code": extract_column_value(column_values, "Owner code"),
            "client_code": extract_column_value(column_values, "Client Code"),
            "deal_status": extract_column_value(column_values, "Deal Status"),
            "close_date_actual": extract_column_value(column_values, "Close Date (A)"),
            "closure_probability": extract_column_value(column_values, "Closure Probability"),
            "deal_value": extract_column_value(column_values, "Masked Deal value"),
            "tentative_close_date": extract_column_value(column_values, "Tentative Close Date"),
            "deal_stage": extract_column_value(column_values, "Deal Stage"),
            "product_deal": extract_column_value(column_values, "Product deal"),
            "sector": extract_column_value(column_values, "Sector/service"),
            "created_date": extract_column_value(column_values, "Created Date"),
        },
        "column_values": column_values  # Preserve full raw data
    }


def map_work_order_item(item: Dict[str, Any]) -> Dict[str, Any]:
    """
    Map a raw Monday.com work order item to structured format
    
    Args:
        item: Raw item from Monday API
        
    Returns:
        Structured work order dict with raw values preserved
    """
    column_values = item.get("column_values", [])
    
    return {
        "id": item.get("id"),
        "item_name": item.get("name"),
        "raw": {
            "deal_name": extract_column_value(column_values, "Deal name masked"),
            "customer_code": extract_column_value(column_values, "Customer Name Code"),
            "serial_number": extract_column_value(column_values, "Serial #"),
            "nature_of_work": extract_column_value(column_values, "Nature of Work"),
            "execution_status": extract_column_value(column_values, "Execution Status"),
            "data_delivery_date": extract_column_value(column_values, "Data Delivery Date"),
            "po_date": extract_column_value(column_values, "Date of PO/LOI"),
            "document_type": extract_column_value(column_values, "Document Type"),
            "probable_start_date": extract_column_value(column_values, "Probable Start Date"),
            "probable_end_date": extract_column_value(column_values, "Probable End Date"),
            "personnel_code": extract_column_value(column_values, "BD/KAM Personnel code"),
            "sector": extract_column_value(column_values, "Sector"),
            "type_of_work": extract_column_value(column_values, "Type of Work"),
            "platform_used": extract_column_value(column_values, "Is any Skylark software platform part of the client deliverables in this deal?"),
            "last_invoice_date": extract_column_value(column_values, "Last invoice date"),
            "latest_invoice_no": extract_column_value(column_values, "latest invoice no."),
            "amount_excl_gst": extract_column_value(column_values, "Amount in Rupees (Excl of GST) (Masked)"),
            "amount_incl_gst": extract_column_value(column_values, "Amount in Rupees (Incl of GST) (Masked)"),
            "billed_value_excl_gst": extract_column_value(column_values, "Billed Value in Rupees (Excl of GST.) (Masked)"),
            "billed_value_incl_gst": extract_column_value(column_values, "Billed Value in Rupees (Incl of GST.) (Masked)"),
            "collected_amount": extract_column_value(column_values, "Collected Amount in Rupees (Incl of GST.) (Masked)"),
            "to_be_billed_excl_gst": extract_column_value(column_values, "Amount to be billed in Rs. (Exl. of GST) (Masked)"),
            "to_be_billed_incl_gst": extract_column_value(column_values, "Amount to be billed in Rs. (Incl. of GST) (Masked)"),
            "amount_receivable": extract_column_value(column_values, "Amount Receivable (Masked)"),
            "ar_priority": extract_column_value(column_values, "AR Priority account"),
            "quantity_by_ops": extract_column_value(column_values, "Quantity by Ops"),
            "quantity_as_per_po": extract_column_value(column_values, "Quantities as per PO"),
            "quantity_billed": extract_column_value(column_values, "Quantity billed (till date)"),
            "balance_quantity": extract_column_value(column_values, "Balance in quantity"),
            "invoice_status": extract_column_value(column_values, "Invoice Status"),
            "expected_billing_month": extract_column_value(column_values, "Expected Billing Month"),
            "actual_billing_month": extract_column_value(column_values, "Actual Billing Month"),
            "actual_collection_month": extract_column_value(column_values, "Actual Collection Month"),
            "wo_status_billed": extract_column_value(column_values, "WO Status (billed)"),
            "collection_status": extract_column_value(column_values, "Collection status"),
            "collection_date": extract_column_value(column_values, "Collection Date"),
            "billing_status": extract_column_value(column_values, "Billing Status"),
        },
        "column_values": column_values  # Preserve full raw data
    }
