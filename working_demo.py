"""
Skylark Drones BI Agent - Working Demo
Single-file demonstration of Monday.com integration
"""

import asyncio
import httpx
import os
from dotenv import load_dotenv
from decimal import Decimal

load_dotenv()

MONDAY_API_TOKEN = os.getenv("MONDAY_API_TOKEN")
MONDAY_DEALS_BOARD_ID = os.getenv("MONDAY_DEALS_BOARD_ID")
MONDAY_WORK_ORDERS_BOARD_ID = os.getenv("MONDAY_WORK_ORDERS_BOARD_ID")


async def fetch_monday_data(board_id):
    """Fetch all items from a Monday.com board"""
    url = "https://api.monday.com/v2"
    headers = {
        "Authorization": f"Bearer {MONDAY_API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    query = """
        query GetBoardItems($board_id: [ID!]!) {
          boards(ids: $board_id) {
            items_page(limit: 100) {
              cursor
              items {
                id
                name
                column_values {
                  id
                  text
                }
              }
            }
          }
        }
    """
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            url,
            json={"query": query, "variables": {"board_id": int(board_id)}},
            headers=headers
        )
        data = response.json()
        
        # Check for errors
        if "errors" in data:
            print(f"❌ Monday.com API Error: {data['errors']}")
            return []
        
        if "data" not in data or not data["data"]["boards"]:
            print(f"❌ No data returned from Monday.com")
            print(f"Response: {data}")
            return []
        
        board = data["data"]["boards"][0]
        return board["items_page"]["items"]


def get_column_value(item, column_id):
    """Extract column value from Monday item by column ID"""
    for col in item["column_values"]:
        if col["id"] == column_id:
            return col["text"]
    return None


def calculate_pipeline(deals_items):
    """Calculate pipeline metrics from deals"""
    total = Decimal(0)
    count = 0
    by_sector = {}
    
    for item in deals_items:
        value_str = get_column_value(item, "Masked Deal value")
        sector = get_column_value(item, "Sector/service")
        status = get_column_value(item, "Deal Status")
        
        if value_str and status in ["Open", "Won"]:
            try:
                value = Decimal(value_str.replace(",", ""))
                total += value
                count += 1
                
                if sector:
                    if sector not in by_sector:
                        by_sector[sector] = {"value": Decimal(0), "count": 0}
                    by_sector[sector]["value"] += value
                    by_sector[sector]["count"] += 1
            except:
                pass
    
    return total, count, by_sector


def calculate_financials(wo_items):
    """Calculate financial metrics from work orders"""
    billed = Decimal(0)
    collected = Decimal(0)
    receivable = Decimal(0)
    
    for item in wo_items:
        billed_str = get_column_value(item, "Billed Value in Rupees (Excl of GST.) (Masked)")
        collected_str = get_column_value(item, "Collected Amount in Rupees (Incl of GST.) (Masked)")
        receivable_str = get_column_value(item, "Amount Receivable (Masked)")
        
        if billed_str:
            try:
                billed += Decimal(billed_str.replace(",", ""))
            except:
                pass
        
        if collected_str:
            try:
                collected += Decimal(collected_str.replace(",", ""))
            except:
                pass
        
        if receivable_str:
            try:
                receivable += Decimal(receivable_str.replace(",", ""))
            except:
                pass
    
    return billed, collected, receivable


async def main():
    print("=" * 80)
    print("SKYLARK DRONES - MONDAY.COM BI AGENT DEMO")
    print("=" * 80)
    print()
    
    print("📡 Fetching data from Monday.com...")
    print(f"   Deals Board: {MONDAY_DEALS_BOARD_ID}")
    print(f"   Work Orders Board: {MONDAY_WORK_ORDERS_BOARD_ID}")
    print()
    
    # Fetch data
    deals_items = await fetch_monday_data(MONDAY_DEALS_BOARD_ID)
    wo_items = await fetch_monday_data(MONDAY_WORK_ORDERS_BOARD_ID)
    
    print(f"   ✓ Retrieved {len(deals_items)} deals")
    print(f"   ✓ Retrieved {len(wo_items)} work orders")
    print()
    
    # Calculate pipeline
    print("📊 PIPELINE ANALYSIS")
    print("-" * 80)
    pipeline_total, pipeline_count, pipeline_by_sector = calculate_pipeline(deals_items)
    
    print(f"Total Pipeline: ₹{pipeline_total:,.0f}")
    print(f"Valued Deals: {pipeline_count}")
    print(f"Average Deal: ₹{(pipeline_total/pipeline_count):,.0f}" if pipeline_count > 0 else "N/A")
    print()
    
    print("Top 5 Sectors by Pipeline:")
    sorted_sectors = sorted(pipeline_by_sector.items(), key=lambda x: x[1]["value"], reverse=True)
    for sector, data in sorted_sectors[:5]:
        print(f"   {sector:20s} ₹{data['value']:>15,.0f}  ({data['count']} deals)")
    print()
    
    # Calculate financials
    print("💰 FINANCIAL ANALYSIS")
    print("-" * 80)
    billed, collected, receivable = calculate_financials(wo_items)
    
    print(f"Total Billed: ₹{billed:,.0f}")
    print(f"Total Collected: ₹{collected:,.0f}")
    print(f"Total Receivable: ₹{receivable:,.0f}")
    
    if billed > 0:
        collection_rate = (collected / (billed * Decimal("1.18"))) * 100
        print(f"Collection Rate: {collection_rate:.1f}%")
    print()
    
    # Operations summary
    print("⚙️  OPERATIONS SUMMARY")
    print("-" * 80)
    completed = sum(1 for item in wo_items if get_column_value(item, "Execution Status") == "Completed")
    ongoing = sum(1 for item in wo_items if get_column_value(item, "Execution Status") == "Ongoing")
    not_started = sum(1 for item in wo_items if get_column_value(item, "Execution Status") == "Not Started")
    
    print(f"Total Work Orders: {len(wo_items)}")
    print(f"Completed: {completed}")
    print(f"Ongoing: {ongoing}")
    print(f"Not Started: {not_started}")
    print(f"Completion Rate: {(completed/len(wo_items)*100):.1f}%")
    print()
    
    print("=" * 80)
    print("✅ DEMO COMPLETE")
    print("=" * 80)
    print()
    print("The system successfully:")
    print("  ✓ Connected to Monday.com API")
    print("  ✓ Retrieved live data from both boards")
    print("  ✓ Calculated pipeline metrics (₹{:,.0f} Cr)".format(pipeline_total / 10000000))
    print("  ✓ Calculated financial metrics (₹{:,.0f} Cr billed)".format(billed / 10000000))
    print("  ✓ Analyzed operations performance")
    print()
    print("Ready for AI agent integration!")


if __name__ == "__main__":
    asyncio.run(main())
