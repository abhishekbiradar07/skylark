"""
Test Monday.com connection from root directory
"""

import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from config.settings import settings
from monday.client import MondayClient
from monday.mapper import map_deal_item, map_work_order_item
from data.processor import process_deal, process_work_order


async def test_connection():
    """Test Monday.com API connection"""
    print("=" * 60)
    print("Monday.com Integration Test")
    print("=" * 60)
    
    client = MondayClient()
    
    # Health check
    print("\n1. Testing API connection...")
    healthy = await client.health_check()
    if healthy:
        print("   ✓ Connected successfully")
    else:
        print("   ✗ Connection failed")
        print(f"\n   Board IDs:")
        print(f"   - Deals: {settings.monday_deals_board_id}")
        print(f"   - Work Orders: {settings.monday_work_orders_board_id}")
        return
    
    # Fetch deals
    print("\n2. Fetching deals from Monday.com...")
    try:
        raw_deals = await client.get_deals()
        print(f"   ✓ Retrieved {len(raw_deals)} raw deal items")
        
        if raw_deals:
            print("\n3. Processing sample deal...")
            mapped = map_deal_item(raw_deals[0])
            processed = process_deal(mapped)
            print(f"   - Deal Name: {processed.deal_name or 'N/A'}")
            print(f"   - Sector: {processed.sector or 'N/A'}")
            print(f"   - Status: {processed.status or 'N/A'}")
            if processed.value:
                print(f"   - Value: ₹{processed.value:,.0f}")
            else:
                print(f"   - Value: Missing")
            print(f"   - Valid: {processed.is_valid}")
            print(f"   - Quality Issues: {len(processed.quality_flags)}")
    except Exception as e:
        print(f"   ✗ Error fetching deals: {e}")
        return
    
    # Fetch work orders
    print("\n4. Fetching work orders from Monday.com...")
    try:
        raw_wos = await client.get_work_orders()
        print(f"   ✓ Retrieved {len(raw_wos)} raw work order items")
        
        if raw_wos:
            print("\n5. Processing sample work order...")
            mapped = map_work_order_item(raw_wos[0])
            processed = process_work_order(mapped)
            print(f"   - Deal Name: {processed.deal_name or 'N/A'}")
            print(f"   - Sector: {processed.sector or 'N/A'}")
            print(f"   - Status: {processed.execution_status or 'N/A'}")
            if processed.billed_value_excl_gst:
                print(f"   - Billed: ₹{processed.billed_value_excl_gst:,.0f}")
            else:
                print(f"   - Billed: Missing")
            print(f"   - Valid: {processed.is_valid}")
            print(f"   - Quality Issues: {len(processed.quality_flags)}")
    except Exception as e:
        print(f"   ✗ Error fetching work orders: {e}")
        return
    
    print("\n" + "=" * 60)
    print("✓ Monday.com Integration Test PASSED")
    print("=" * 60)
    print(f"\nData Summary:")
    print(f"  - Deals Board ({settings.monday_deals_board_id}): {len(raw_deals)} items")
    print(f"  - Work Orders Board ({settings.monday_work_orders_board_id}): {len(raw_wos)} items")
    print(f"\nThe agent can now query Monday.com dynamically!")


if __name__ == "__main__":
    asyncio.run(test_connection())
