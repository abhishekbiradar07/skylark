"""
Simple working demo using Excel data to show analytics
"""

import pandas as pd
from decimal import Decimal

print("=" * 80)
print("SKYLARK DRONES - BI AGENT DEMO (Excel Data)")
print("=" * 80)
print()

# Load Excel data
print("📂 Loading data from Excel files...")
deals_df = pd.read_excel('Deal funnel Data.xlsx')
wo_df = pd.read_excel('Work_Order_Tracker Data.xlsx')

# Work orders: first row is header
wo_df.columns = wo_df.iloc[0]
wo_df = wo_df[1:].reset_index(drop=True)

print(f"   ✓ Loaded {len(deals_df)} deals")
print(f"   ✓ Loaded {len(wo_df)} work orders")
print()

# Calculate pipeline
print("📊 PIPELINE ANALYSIS")
print("-" * 80)

valued_deals = deals_df[deals_df['Masked Deal value'].notna() & (deals_df['Masked Deal value'] != '')]
open_won_deals = valued_deals[valued_deals['Deal Status'].isin(['Open', 'Won'])]

pipeline_total = open_won_deals['Masked Deal value'].astype(float).sum()
pipeline_count = len(open_won_deals)

print(f"Total Pipeline: ₹{pipeline_total:,.0f}")
print(f"Valued Deals: {pipeline_count}")
if pipeline_count > 0:
    print(f"Average Deal: ₹{(pipeline_total/pipeline_count):,.0f}")
print()

# By sector
print("Top Sectors by Pipeline:")
sector_pipeline = open_won_deals.groupby('Sector/service')['Masked Deal value'].agg(['sum', 'count'])
sector_pipeline = sector_pipeline.sort_values('sum', ascending=False).head(5)

for sector, row in sector_pipeline.iterrows():
    print(f"   {str(sector):20s} ₹{row['sum']:>15,.0f}  ({int(row['count'])} deals)")
print()

# Financial analysis
print("💰 FINANCIAL ANALYSIS")
print("-" * 80)

billed_col = 'Billed Value in Rupees (Excl of GST.) (Masked)'
collected_col = 'Collected Amount in Rupees (Incl of GST.) (Masked)'
receivable_col = 'Amount Receivable (Masked)'

billed_total = pd.to_numeric(wo_df[billed_col], errors='coerce').sum()
collected_total = pd.to_numeric(wo_df[collected_col], errors='coerce').sum()
receivable_total = pd.to_numeric(wo_df[receivable_col], errors='coerce').sum()

print(f"Total Billed: ₹{billed_total:,.0f}")
print(f"Total Collected: ₹{collected_total:,.0f}")
print(f"Total Receivable: ₹{receivable_total:,.0f}")

if billed_total > 0:
    # Approximate collection rate (collected incl GST vs billed excl GST * 1.18)
    collection_rate = (collected_total / (billed_total * 1.18)) * 100
    print(f"Collection Rate: {collection_rate:.1f}%")
print()

# Operations
print("⚙️  OPERATIONS SUMMARY")
print("-" * 80)

total_wos = len(wo_df)
completed = len(wo_df[wo_df['Execution Status'] == 'Completed'])
ongoing = len(wo_df[wo_df['Execution Status'] == 'Ongoing'])
not_started = len(wo_df[wo_df['Execution Status'] == 'Not Started'])

print(f"Total Work Orders: {total_wos}")
print(f"Completed: {completed}")
print(f"Ongoing: {ongoing}")
print(f"Not Started: {not_started}")
print(f"Completion Rate: {(completed/total_wos*100):.1f}%")
print()

# Sector comparison
print("🔄 CROSS-BOARD SECTOR ANALYSIS")
print("-" * 80)

# Pipeline by sector
deal_sectors = open_won_deals.groupby('Sector/service')['Masked Deal value'].agg(['sum', 'count'])
deal_sectors.columns = ['pipeline', 'deal_count']

# Operations by sector
wo_sectors = wo_df.groupby('Sector').size()
wo_billed = wo_df.groupby('Sector')[billed_col].apply(lambda x: pd.to_numeric(x, errors='coerce').sum())

for sector in ['Mining', 'Renewables', 'Railways']:
    print(f"\n{sector}:")
    if sector in deal_sectors.index:
        print(f"   Pipeline: ₹{deal_sectors.loc[sector, 'pipeline']:,.0f} ({int(deal_sectors.loc[sector, 'deal_count'])} deals)")
    else:
        print(f"   Pipeline: No data")
    
    if sector in wo_billed.index:
        print(f"   Execution: ₹{wo_billed[sector]:,.0f} ({wo_sectors[sector]} WOs)")
    else:
        print(f"   Execution: No data")
print()

# Data quality
print("⚠️  DATA QUALITY SUMMARY")
print("-" * 80)

missing_deal_values = len(deals_df) - pipeline_count
missing_billed = wo_df[billed_col].isna().sum()
missing_collected = wo_df[collected_col].isna().sum()

print(f"• {missing_deal_values} deals missing values ({missing_deal_values/len(deals_df)*100:.1f}%)")
print(f"• {missing_billed} work orders missing billed value ({missing_billed/len(wo_df)*100:.1f}%)")
print(f"• {missing_collected} work orders missing collected amount ({missing_collected/len(wo_df)*100:.1f}%)")
print()

print("=" * 80)
print("✅ DEMO COMPLETE")
print("=" * 80)
print()
print("System capabilities demonstrated:")
print("  ✓ Data processing with missing value handling")
print("  ✓ Pipeline calculations (₹{:.1f} Cr)".format(pipeline_total / 10000000))
print("  ✓ Financial metrics (₹{:.1f} Cr billed)".format(billed_total / 10000000))
print("  ✓ Operations analysis ({:.1f}% completion rate)".format(completed/total_wos*100))
print("  ✓ Cross-board sector analysis")
print("  ✓ Data quality transparency")
print()
print("Note: This demo uses Excel data. The production system queries Monday.com live!")
