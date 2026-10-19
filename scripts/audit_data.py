"""
Data Audit Script for Skylark Drones Monday.com BI Agent
Analyzes Excel files to understand data quality and structure
"""

import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path

def audit_deals():
    """Audit the Deals dataset"""
    print("=" * 80)
    print("DEALS DATASET AUDIT")
    print("=" * 80)
    
    df = pd.read_excel('Deal funnel Data.xlsx')
    
    print(f"\n1. BASIC INFO")
    print(f"   Rows: {len(df)}")
    print(f"   Columns: {len(df.columns)}")
    print(f"   Column names: {list(df.columns)}")
    
    print(f"\n2. MISSING VALUES")
    missing = df.isnull().sum()
    missing_pct = (missing / len(df) * 100).round(1)
    for col in df.columns:
        if missing[col] > 0:
            print(f"   {col}: {missing[col]} ({missing_pct[col]}%)")
    
    print(f"\n3. SECTOR/SERVICE ANALYSIS")
    sectors = df['Sector/service'].value_counts(dropna=False)
    print(f"   Unique sectors: {df['Sector/service'].nunique()}")
    print(f"   Sector distribution:")
    for sector, count in sectors.items():
        print(f"      {sector}: {count}")
    
    print(f"\n4. DEAL STATUS ANALYSIS")
    statuses = df['Deal Status'].value_counts(dropna=False)
    for status, count in statuses.items():
        print(f"   {status}: {count}")
    
    print(f"\n5. DEAL STAGE ANALYSIS")
    stages = df['Deal Stage'].value_counts(dropna=False)
    for stage, count in stages.items():
        print(f"   {stage}: {count}")
    
    print(f"\n6. CLOSURE PROBABILITY ANALYSIS")
    probs = df['Closure Probability'].value_counts(dropna=False)
    for prob, count in probs.items():
        print(f"   {prob}: {count}")
    
    print(f"\n7. DEAL VALUE ANALYSIS")
    valid_values = df['Masked Deal value'].dropna()
    print(f"   Non-null values: {len(valid_values)}")
    print(f"   Null values: {df['Masked Deal value'].isnull().sum()}")
    if len(valid_values) > 0:
        print(f"   Min: ₹{valid_values.min():,.0f}")
        print(f"   Max: ₹{valid_values.max():,.0f}")
        print(f"   Mean: ₹{valid_values.mean():,.0f}")
        print(f"   Median: ₹{valid_values.median():,.0f}")
        print(f"   Total: ₹{valid_values.sum():,.0f}")
    
    print(f"\n8. DATE FIELDS")
    date_cols = ['Close Date (A)', 'Tentative Close Date', 'Created Date']
    for col in date_cols:
        non_null = df[col].notna().sum()
        print(f"   {col}: {non_null} non-null values")
    
    print(f"\n9. OWNER ANALYSIS")
    owners = df['Owner code'].value_counts(dropna=False)
    print(f"   Unique owners: {df['Owner code'].nunique()}")
    print(f"   Top 5 owners:")
    for owner, count in owners.head(5).items():
        print(f"      {owner}: {count} deals")
    
    print(f"\n10. PRODUCT DEAL ANALYSIS")
    products = df['Product deal'].value_counts(dropna=False)
    for prod, count in products.items():
        print(f"   {prod}: {count}")
    
    return df

def audit_work_orders():
    """Audit the Work Orders dataset"""
    print("\n" + "=" * 80)
    print("WORK ORDERS DATASET AUDIT")
    print("=" * 80)
    
    df = pd.read_excel('Work_Order_Tracker Data.xlsx')
    
    # First row contains headers
    df.columns = df.iloc[0]
    df = df[1:].reset_index(drop=True)
    
    print(f"\n1. BASIC INFO")
    print(f"   Rows: {len(df)}")
    print(f"   Columns: {len(df.columns)}")
    print(f"   Column names: {list(df.columns)}")
    
    print(f"\n2. KEY COLUMNS MISSING VALUES")
    key_cols = ['Deal name masked', 'Sector', 'Execution Status', 'Billed Value in Rupees (Excl of GST.) (Masked)', 
                'Collected Amount in Rupees (Incl of GST.) (Masked)', 'Amount Receivable (Masked)']
    for col in key_cols:
        if col in df.columns:
            missing = df[col].isnull().sum()
            missing_pct = (missing / len(df) * 100).round(1)
            print(f"   {col}: {missing} ({missing_pct}%)")
    
    print(f"\n3. SECTOR ANALYSIS")
    if 'Sector' in df.columns:
        sectors = df['Sector'].value_counts(dropna=False)
        print(f"   Unique sectors: {df['Sector'].nunique()}")
        print(f"   Sector distribution:")
        for sector, count in sectors.items():
            print(f"      {sector}: {count}")
    
    print(f"\n4. EXECUTION STATUS")
    if 'Execution Status' in df.columns:
        statuses = df['Execution Status'].value_counts(dropna=False)
        for status, count in statuses.items():
            print(f"   {status}: {count}")
    
    print(f"\n5. FINANCIAL METRICS")
    
    # Billed Value
    if 'Billed Value in Rupees (Excl of GST.) (Masked)' in df.columns:
        col = 'Billed Value in Rupees (Excl of GST.) (Masked)'
        valid = pd.to_numeric(df[col], errors='coerce').dropna()
        print(f"   Billed Value (Excl GST):")
        print(f"      Non-null: {len(valid)}")
        if len(valid) > 0:
            print(f"      Total: ₹{valid.sum():,.0f}")
    
    # Collected Amount
    if 'Collected Amount in Rupees (Incl of GST.) (Masked)' in df.columns:
        col = 'Collected Amount in Rupees (Incl of GST.) (Masked)'
        valid = pd.to_numeric(df[col], errors='coerce').dropna()
        print(f"   Collected Amount (Incl GST):")
        print(f"      Non-null: {len(valid)}")
        if len(valid) > 0:
            print(f"      Total: ₹{valid.sum():,.0f}")
    
    # Receivables
    if 'Amount Receivable (Masked)' in df.columns:
        col = 'Amount Receivable (Masked)'
        valid = pd.to_numeric(df[col], errors='coerce').dropna()
        print(f"   Amount Receivable:")
        print(f"      Non-null: {len(valid)}")
        if len(valid) > 0:
            print(f"      Total: ₹{valid.sum():,.0f}")
    
    print(f"\n6. DATE FIELDS")
    date_cols = ['Data Delivery Date', 'Date of PO/LOI', 'Probable Start Date', 'Probable End Date']
    for col in date_cols:
        if col in df.columns:
            non_null = df[col].notna().sum()
            print(f"   {col}: {non_null} non-null values")
    
    print(f"\n7. NATURE OF WORK")
    if 'Nature of Work' in df.columns:
        nature = df['Nature of Work'].value_counts(dropna=False)
        for nat, count in nature.items():
            print(f"   {nat}: {count}")
    
    return df

if __name__ == "__main__":
    deals_df = audit_deals()
    wo_df = audit_work_orders()
    
    print("\n" + "=" * 80)
    print("CROSS-DATASET ANALYSIS")
    print("=" * 80)
    
    print(f"\n1. SECTOR COMPARISON")
    print(f"   Deals sectors: {set(deals_df['Sector/service'].dropna().unique())}")
    print(f"   Work Orders sectors: {set(wo_df['Sector'].dropna().unique())}")
    
    print(f"\n2. POTENTIAL JOIN KEY ANALYSIS")
    print(f"   Deals 'Deal Name' unique values: {deals_df['Deal Name'].nunique()}")
    print(f"   Work Orders 'Deal name masked' unique values: {wo_df['Deal name masked'].nunique()}")
    print(f"   Note: Deal-level joins may be unreliable. Use sector-level analysis for cross-board queries.")
    
    print("\n" + "=" * 80)
    print("AUDIT COMPLETE")
    print("=" * 80)
