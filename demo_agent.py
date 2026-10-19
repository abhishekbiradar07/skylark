"""
Skylark Drones BI Agent - Demo Script
Demonstrates full Monday.com integration and analytics
"""

import asyncio
import sys
import os
from decimal import Decimal

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from config.settings import settings
from monday.client import MondayClient
from monday.mapper import map_deal_item, map_work_order_item
from data.processor import process_deals, process_work_orders
from analytics.pipeline import calculate_pipeline, get_current_quarter
from analytics.finance import calculate_financial_metrics
from analytics.operations import calculate_operations_metrics
from analytics.cross_board import analyze_all_sectors


async def main():
    """Run the BI Agent demo"""
    
    print("=" * 80)
    print("SKYLARK DRONES - MONDAY.COM BUSINESS INTELLIGENCE AGENT")
    print("=" * 80)
    print()
    
    # Initialize client
    client = MondayClient()
    
    # Step 1: Fetch raw data from Monday.com
    print("📡 Step 1: Fetching data from Monday.com...")
    print(f"   Deals Board: {settings.monday_deals_board_id}")
    print(f"   Work Orders Board: {settings.monday_work_orders_board_id}")
    print()
    
    raw_deals = await client.get_deals()
    raw_wos = await client.get_work_orders()
    
    print(f"   ✓ Retrieved {len(raw_deals)} deals")
    print(f"   ✓ Retrieved {len(raw_wos)} work orders")
    print()
    
    # Step 2: Map and normalize data
    print("🧹 Step 2: Processing and normalizing data...")
    mapped_deals = [map_deal_item(d) for d in raw_deals]
    mapped_wos = [map_work_order_item(wo) for wo in raw_wos]
    
    deals = process_deals(mapped_deals)
    work_orders = process_work_orders(mapped_wos)
    
    print(f"   ✓ Processed {len(deals)} valid deals")
    print(f"   ✓ Processed {len(work_orders)} valid work orders")
    print()
    
    # Step 3: Calculate pipeline metrics
    print("📊 Step 3: Calculating pipeline metrics...")
    pipeline = calculate_pipeline(deals, status_filter=["Open", "Won"])
    
    print(f"\n   PIPELINE ANALYSIS")
    print(f"   " + "-" * 60)
    print(f"   Total Deals: {pipeline.total_deals}")
    print(f"   Valued Deals: {pipeline.valued_deals}")
    print(f"   Excluded (no value): {pipeline.excluded_deals}")
    print(f"   Known Pipeline: ₹{pipeline.known_pipeline:,.0f}")
    print(f"   Weighted Pipeline: ₹{pipeline.weighted_pipeline:,.0f}")
    print()
    
    if pipeline.by_sector:
        print(f"   By Sector:")
        for sector, metrics in sorted(pipeline.by_sector.items(), key=lambda x: x[1]['known_pipeline'], reverse=True)[:5]:
            print(f"      {sector}: ₹{metrics['known_pipeline']:,.0f} ({metrics['deals']} deals)")
    print()
    
    # Step 4: Calculate financial metrics
    print("💰 Step 4: Calculating financial metrics...")
    finance = calculate_financial_metrics(work_orders)
    
    print(f"\n   FINANCIAL ANALYSIS")
    print(f"   " + "-" * 60)
    print(f"   Total Work Orders: {finance.total_work_orders}")
    print(f"   Billed Work Orders: {finance.billed_work_orders}")
    print(f"   Total Billed: ₹{finance.total_billed:,.0f}")
    print(f"   Total Collected: ₹{finance.total_collected:,.0f}")
    print(f"   Total Receivable: ₹{finance.total_receivable:,.0f}")
    if finance.collection_rate:
        print(f"   Collection Rate: {finance.collection_rate:.1f}%")
    print()
    
    # Step 5: Calculate operations metrics
    print("⚙️  Step 5: Calculating operations metrics...")
    ops = calculate_operations_metrics(work_orders)
    
    print(f"\n   OPERATIONS ANALYSIS")
    print(f"   " + "-" * 60)
    print(f"   Total Work Orders: {ops.total_work_orders}")
    print(f"   Active: {ops.active_work_orders}")
    print(f"   Completed: {ops.completed_work_orders}")
    print(f"   Delayed: {ops.delayed_work_orders}")
    print()
    
    # Step 6: Cross-board sector analysis
    print("🔄 Step 6: Cross-board sector analysis...")
    sectors = analyze_all_sectors(deals, work_orders)
    
    print(f"\n   SECTOR PERFORMANCE")
    print(f"   " + "-" * 60)
    for sector, analysis in list(sectors.items())[:5]:
        print(f"\n   {sector}:")
        print(f"      Pipeline: ₹{analysis.pipeline_value:,.0f} ({analysis.deals_count} deals)")
        print(f"      Execution: ₹{analysis.billed_value:,.0f} ({analysis.work_orders_count} WOs)")
        print(f"      Strength: Pipeline={analysis.pipeline_strength}, Execution={analysis.execution_strength}")
    print()
    
    # Step 7: Data quality summary
    print("⚠️  Step 7: Data quality summary...")
    print(f"\n   DATA QUALITY")
    print(f"   " + "-" * 60)
    for issue in pipeline.data_quality_summary:
        print(f"      • {issue}")
    for issue in finance.data_quality_summary:
        print(f"      • {issue}")
    print()
    
    print("=" * 80)
    print("✅ DEMO COMPLETE - All systems operational!")
    print("=" * 80)
    print()
    print("The agent can now answer executive questions like:")
    print("  • 'What is our current pipeline?'")
    print("  • 'How much pipeline do we have in Mining?'")
    print("  • 'Which projects are delayed?'")
    print("  • 'How much have we billed and collected?'")
    print("  • 'Compare Mining and Renewables sectors'")
    print()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()
