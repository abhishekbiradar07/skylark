"""
Tool definitions and execution for the BI Agent
"""

import sys
import os

# Add backend to path for imports
backend_path = os.path.join(os.path.dirname(__file__), '..')
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from typing import Dict, Any, List
from decimal import Decimal

# Use absolute imports from backend root
import monday.client
import monday.mapper
import data.processor
import analytics.pipeline
import analytics.finance
import analytics.operations
import analytics.cross_board

from monday.client import MondayClient
from monday.mapper import map_deal_item, map_work_order_item
from data.processor import process_deals, process_work_orders
from analytics.pipeline import calculate_pipeline, get_top_opportunities
from analytics.finance import calculate_financial_metrics, get_top_receivables
from analytics.operations import calculate_operations_metrics, get_delayed_work_orders
from analytics.cross_board import analyze_sector_performance, compare_sectors, analyze_all_sectors


# Tool definitions in OpenAI function format
AVAILABLE_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_pipeline_metrics",
            "description": "Calculate pipeline metrics including total pipeline, weighted pipeline, deal counts. Can filter by sector or quarter. Call without parameters to get all data.",
            "parameters": {
                "type": "object",
                "properties": {},
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_financial_metrics",
            "description": "Calculate financial metrics including billed value, collected amount, receivables, collection rate. Call without parameters to get all data.",
            "parameters": {
                "type": "object",
                "properties": {},
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_operations_metrics",
            "description": "Calculate operations metrics including work order counts, completion rates, delayed projects. Call without parameters to get all data.",
            "parameters": {
                "type": "object",
                "properties": {},
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "compare_sectors",
            "description": "Compare two sectors across pipeline and execution metrics.",
            "parameters": {
                "type": "object",
                "properties": {
                    "sector1": {
                        "type": "string",
                        "description": "First sector to compare"
                    },
                    "sector2": {
                        "type": "string",
                        "description": "Second sector to compare"
                    }
                },
                "required": ["sector1", "sector2"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_all_sectors",
            "description": "Get list of all available sectors in the data.",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_delayed_projects",
            "description": "Get list of delayed work orders/projects.",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    }
]


# Global cache for data (to avoid re-fetching)
_data_cache = {
    "deals": None,
    "work_orders": None
}


async def _ensure_data_loaded():
    """Ensure data is loaded from Monday.com"""
    if _data_cache["deals"] is None or _data_cache["work_orders"] is None:
        client = MondayClient()
        
        # Fetch from Monday
        raw_deals = await client.get_deals()
        raw_wos = await client.get_work_orders()
        
        # Map and process
        mapped_deals = [map_deal_item(d) for d in raw_deals]
        mapped_wos = [map_work_order_item(wo) for wo in raw_wos]
        
        _data_cache["deals"] = process_deals(mapped_deals)
        _data_cache["work_orders"] = process_work_orders(mapped_wos)
    
    return _data_cache["deals"], _data_cache["work_orders"]


async def execute_tool(tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
    """Execute a tool and return structured results"""
    
    # Load data
    deals, work_orders = await _ensure_data_loaded()
    
    if tool_name == "get_pipeline_metrics":
        sector = args.get("sector")
        quarter = args.get("quarter")
        
        metrics = calculate_pipeline(
            deals,
            sector_filter=sector,
            quarter=quarter
        )
        
        return {
            "metrics": [
                {"label": "Total Deals", "value": metrics.total_deals},
                {"label": "Valued Deals", "value": metrics.valued_deals},
                {"label": "Known Pipeline", "value": f"₹{metrics.known_pipeline:,.0f}"},
                {"label": "Weighted Pipeline", "value": f"₹{metrics.weighted_pipeline:,.0f}"}
            ],
            "by_sector": metrics.by_sector,
            "by_stage": metrics.by_stage,
            "data_quality": metrics.data_quality_summary,
            "insights": [
                f"Average deal value: ₹{metrics.known_pipeline / metrics.valued_deals:,.0f}" if metrics.valued_deals > 0 else "No valued deals"
            ]
        }
    
    elif tool_name == "get_financial_metrics":
        sector = args.get("sector")
        
        metrics = calculate_financial_metrics(work_orders, sector_filter=sector)
        
        return {
            "metrics": [
                {"label": "Total Billed", "value": f"₹{metrics.total_billed:,.0f}"},
                {"label": "Total Collected", "value": f"₹{metrics.total_collected:,.0f}"},
                {"label": "Total Receivable", "value": f"₹{metrics.total_receivable:,.0f}"},
                {"label": "Collection Rate", "value": f"{metrics.collection_rate:.1f}%" if metrics.collection_rate else "N/A"}
            ],
            "by_sector": metrics.by_sector,
            "data_quality": metrics.data_quality_summary
        }
    
    elif tool_name == "get_operations_metrics":
        sector = args.get("sector")
        
        metrics = calculate_operations_metrics(work_orders, sector_filter=sector)
        
        return {
            "metrics": [
                {"label": "Total Work Orders", "value": metrics.total_work_orders},
                {"label": "Active", "value": metrics.active_work_orders},
                {"label": "Completed", "value": metrics.completed_work_orders},
                {"label": "Delayed", "value": metrics.delayed_work_orders}
            ],
            "by_sector": metrics.by_sector,
            "by_status": metrics.by_status,
            "delayed_projects": metrics.delayed_projects,
            "data_quality": metrics.data_quality_summary,
            "insights": [
                f"Completion rate: {metrics.completed_work_orders / metrics.total_work_orders * 100:.1f}%" if metrics.total_work_orders > 0 else "No work orders"
            ]
        }
    
    elif tool_name == "compare_sectors":
        sector1 = args["sector1"]
        sector2 = args["sector2"]
        
        comparison = compare_sectors(deals, work_orders, sector1, sector2)
        
        return {
            "comparison": {
                sector1: {
                    "deals": comparison[sector1].deals_count,
                    "pipeline": f"₹{comparison[sector1].pipeline_value:,.0f}",
                    "work_orders": comparison[sector1].work_orders_count,
                    "billed": f"₹{comparison[sector1].billed_value:,.0f}",
                    "pipeline_strength": comparison[sector1].pipeline_strength,
                    "execution_strength": comparison[sector1].execution_strength
                },
                sector2: {
                    "deals": comparison[sector2].deals_count,
                    "pipeline": f"₹{comparison[sector2].pipeline_value:,.0f}",
                    "work_orders": comparison[sector2].work_orders_count,
                    "billed": f"₹{comparison[sector2].billed_value:,.0f}",
                    "pipeline_strength": comparison[sector2].pipeline_strength,
                    "execution_strength": comparison[sector2].execution_strength
                }
            },
            "insights": [
                f"{sector1} pipeline strength: {comparison[sector1].pipeline_strength}",
                f"{sector2} pipeline strength: {comparison[sector2].pipeline_strength}",
                f"{sector1} execution strength: {comparison[sector1].execution_strength}",
                f"{sector2} execution strength: {comparison[sector2].execution_strength}"
            ]
        }
    
    elif tool_name == "get_all_sectors":
        sectors = set(d.sector for d in deals if d.sector)
        
        return {
            "sectors": sorted(list(sectors)),
            "insights": [f"Found {len(sectors)} sectors in the data"]
        }
    
    elif tool_name == "get_delayed_projects":
        delayed = get_delayed_work_orders(work_orders)
        
        return {
            "metrics": [
                {"label": "Delayed Projects", "value": len(delayed)}
            ],
            "delayed_list": [
                {
                    "deal_name": wo.deal_name,
                    "sector": wo.sector,
                    "status": wo.execution_status
                }
                for wo in delayed[:10]  # Limit to 10
            ],
            "insights": [
                f"{len(delayed)} projects are delayed or not started"
            ]
        }
    
    else:
        return {"error": f"Unknown tool: {tool_name}"}
