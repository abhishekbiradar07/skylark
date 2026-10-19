"""
Quick test script to verify Monday.com connectivity
"""

import asyncio
import sys
sys.path.insert(0, '.')

from monday.client import monday_client
from monday.mapper import map_deal_item, map_work_order_item
from data.processor import process_deal, process_work_order


async def test_connection():
    """Test Monday.com API connection"""
    print("Testing Monday.com API connection...\n")
    
    # Health check
    print("1. Health check...")
    healthy = await monday_client.health_check()
    print(f"   Status: {'✓ Connected' if healthy else '✗ Failed'}\n")
    
    if not healthy:
        print("Cannot connect to Monday.com. Check your API token and board IDs.")
        return
    
    # Fetch deals
    print("2. Fetching deals...")
    raw_deals = await monday_client.get_deals()
    print(f"   Retrieved {len(raw_deals)} raw deal items\n")
    
    if raw_deals:
        print("3. Processing first deal...")
        mapped = map_deal_item(raw_deals[0])
        processed = process_deal(mapped)
        print(f"   Deal: {processed.deal_name}")
        print(f"   Sector: {processed.sector}")
        print(f"   Status: {processed.status}")
        print(f"   Value: ₹{processed.value:,.0f}" if processed.value else "   Value: Missing")
        print(f"   Valid: {processed.is_valid}")
        print(f"   Quality Flags: {len(processed.quality_flags)}\n")
    
    # Fetch work orders
    print("4. Fetching work orders...")
    raw_wos = await monday_client.get_work_orders()
    print(f"   Retrieved {len(raw_wos)} raw work order items\n")
    
    if raw_wos:
        print("5. Processing first work order...")
        mapped = map_work_order_item(raw_wos[0])
        processed = process_work_order(mapped)
        print(f"   Deal: {processed.deal_name}")
        print(f"   Sector: {processed.sector}")
        print(f"   Status: {processed.execution_status}")
        print(f"   Billed: ₹{processed.billed_value_excl_gst:,.0f}" if processed.billed_value_excl_gst else "   Billed: Missing")
        print(f"   Valid: {processed.is_valid}")
        print(f"   Quality Flags: {len(processed.quality_flags)}\n")
    
    print("✓ Monday.com integration test complete!")
    print(f"  Deals board: {len(raw_deals)} items")
    print(f"  Work Orders board: {len(raw_wos)} items")


if __name__ == "__main__":
    asyncio.run(test_connection())
