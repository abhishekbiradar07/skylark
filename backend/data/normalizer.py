"""
Dynamic data normalization engine
Cleans and standardizes raw Monday.com data in-memory
NEVER writes back to Monday
"""

from typing import Optional, Any
from datetime import datetime
from decimal import Decimal, InvalidOperation
from dateutil import parser
import re


def normalize_text(value: Optional[str]) -> Optional[str]:
    """Trim and normalize text fields"""
    if not value or not isinstance(value, str):
        return None
    
    normalized = value.strip()
    return normalized if normalized else None


def normalize_sector(value: Optional[str]) -> Optional[str]:
    """
    Normalize sector/service values to canonical form
    Based on actual data patterns from audit
    """
    if not value:
        return None
    
    normalized = normalize_text(value)
    if not normalized:
        return None
    
    # Convert to title case
    normalized = normalized.title()
    
    # Handle known variations
    sector_map = {
        "Mining": "Mining",
        "Renewables": "Renewables",
        "Railways": "Railways",
        "Powerline": "Powerline",
        "Others": "Others",
        "Construction": "Construction",
        "Dsp": "DSP",
        "Tender": "Tender",
        "Manufacturing": "Manufacturing",
        "Security And Surveillance": "Security and Surveillance",
        "Aviation": "Aviation",
    }
    
    return sector_map.get(normalized, normalized)


def normalize_status(value: Optional[str]) -> Optional[str]:
    """Normalize status fields"""
    if not value:
        return None
    
    normalized = normalize_text(value)
    if not normalized:
        return None
    
    # Common status patterns
    status_map = {
        "won": "Won",
        "dead": "Dead",
        "open": "Open",
        "on hold": "On Hold",
        "completed": "Completed",
        "ongoing": "Ongoing",
        "not started": "Not Started",
        "pause / struck": "Pause / Struck",
        "partial completed": "Partial Completed",
    }
    
    lower = normalized.lower()
    return status_map.get(lower, normalized)


def normalize_probability(value: Optional[str]) -> tuple[Optional[str], Optional[float]]:
    """
    Normalize closure probability to text and numeric form
    
    Returns:
        Tuple of (normalized_text, numeric_value)
    """
    if not value:
        return None, None
    
    normalized = normalize_text(value)
    if not normalized:
        return None, None
    
    # Probability mapping based on business rules
    prob_map = {
        "high": ("High", 0.7),
        "medium": ("Medium", 0.5),
        "low": ("Low", 0.3),
    }
    
    lower = normalized.lower()
    if lower in prob_map:
        return prob_map[lower]
    
    return normalized, None


def normalize_currency(value: Optional[str]) -> Optional[Decimal]:
    """
    Parse currency string to Decimal
    Handles various formats: "1000", "1,000", "1000.00"
    """
    if not value:
        return None
    
    if isinstance(value, (int, float)):
        try:
            return Decimal(str(value))
        except (InvalidOperation, ValueError):
            return None
    
    if not isinstance(value, str):
        return None
    
    # Remove whitespace and commas
    cleaned = value.strip().replace(",", "")
    
    if not cleaned:
        return None
    
    try:
        decimal_value = Decimal(cleaned)
        # Sanity check: negative values are suspicious
        if decimal_value < 0:
            return None
        return decimal_value
    except (InvalidOperation, ValueError):
        return None


def normalize_number(value: Optional[str]) -> Optional[float]:
    """Parse numeric string to float"""
    if not value:
        return None
    
    if isinstance(value, (int, float)):
        return float(value)
    
    if not isinstance(value, str):
        return None
    
    cleaned = value.strip().replace(",", "")
    
    if not cleaned:
        return None
    
    try:
        return float(cleaned)
    except ValueError:
        return None


def normalize_date(value: Optional[str]) -> Optional[datetime]:
    """
    Parse date string to datetime
    Handles multiple formats flexibly
    """
    if not value:
        return None
    
    if isinstance(value, datetime):
        return value
    
    if not isinstance(value, str):
        return None
    
    cleaned = value.strip()
    
    if not cleaned:
        return None
    
    try:
        # Use dateutil parser for flexible date parsing
        return parser.parse(cleaned)
    except (ValueError, parser.ParserError):
        return None


def is_header_fragment(value: Optional[str], column_name: str) -> bool:
    """
    Detect if a value is actually a header fragment
    (e.g., "Deal Status" appearing as a value in Deal Status column)
    """
    if not value or not isinstance(value, str):
        return False
    
    # Check if value matches common header patterns
    header_patterns = [
        "Deal Name",
        "Deal Status",
        "Deal Stage",
        "Closure Probability",
        "Product deal",
        "Sector/service",
        "Owner code",
        "Serial #",
        "Execution Status",
    ]
    
    return value.strip() in header_patterns


def detect_quality_issues(raw_value: Any, normalized_value: Any, field_name: str) -> list[dict]:
    """
    Detect data quality issues
    
    Returns:
        List of quality issue dicts
    """
    issues = []
    
    # Missing value
    if raw_value in [None, "", " "]:
        issues.append({
            "field": field_name,
            "issue": "MISSING_VALUE",
            "severity": "warning"
        })
    
    # Failed normalization
    elif raw_value and not normalized_value:
        issues.append({
            "field": field_name,
            "issue": "NORMALIZATION_FAILED",
            "severity": "warning",
            "raw_value": str(raw_value)[:50]  # Truncate long values
        })
    
    return issues


def normalize_stage(value: Optional[str]) -> Optional[str]:
    """Normalize deal stage (preserve as-is, just clean)"""
    return normalize_text(value)


def normalize_execution_status(value: Optional[str]) -> Optional[str]:
    """Normalize work order execution status"""
    if not value:
        return None
    
    normalized = normalize_text(value)
    if not normalized:
        return None
    
    # Execution status patterns
    status_map = {
        "completed": "Completed",
        "ongoing": "Ongoing",
        "not started": "Not Started",
        "pause / struck": "Pause / Struck",
        "partial completed": "Partial Completed",
        "executed until current month": "Executed until current month",
        "details pending from client": "Details pending from Client",
    }
    
    lower = normalized.lower()
    return status_map.get(lower, normalized)


def normalize_nature_of_work(value: Optional[str]) -> Optional[str]:
    """Normalize nature of work field"""
    if not value:
        return None
    
    normalized = normalize_text(value)
    if not normalized:
        return None
    
    # Nature patterns
    nature_map = {
        "one time project": "One time Project",
        "proof of concept": "Proof of Concept",
        "annual rate contract": "Annual Rate Contract",
        "monthly contract": "Monthly Contract",
    }
    
    lower = normalized.lower()
    return nature_map.get(lower, normalized)
