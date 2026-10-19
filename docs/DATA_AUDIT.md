# Data Audit Report - Skylark Drones Monday.com Boards

**Date:** August 25, 2026  
**Auditor:** System  
**Source:** Deal funnel Data.xlsx, Work_Order_Tracker Data.xlsx  
**Monday.com Boards:** Deals (5030845871), Work Orders (5030845875)

---

## Executive Summary

The Monday.com boards contain real-world messy business data requiring robust data quality handling:

- **Deals:** 346 records with 52.3% missing deal values
- **Work Orders:** 176 records with 35.8% missing billed values
- **Key Finding:** Deal-level joins between boards are unreliable; sector-level analysis is recommended
- **Data Quality:** Significant missing values across critical financial fields

---

## 1. DEALS BOARD ANALYSIS

### Basic Statistics
- **Total Records:** 346
- **Columns:** 12
- **Date Range:** Created dates from 2025-2026

### Column Schema
```
Deal Name                - Text (primary identifier)
Owner code               - Text (BD/KAM personnel)
Client Code              - Text (client identifier)
Deal Status              - Status (Won/Dead/Open/On Hold)
Close Date (A)           - Date (actual close date)
Closure Probability      - Text (High/Medium/Low)
Masked Deal value        - Number (deal value in INR)
Tentative Close Date     - Date (expected close)
Deal Stage               - Stage (A-O stages)
Product deal             - Text (product mix)
Sector/service           - Text (industry sector)
Created Date             - Date (deal creation)
```

### Data Quality Issues

#### Missing Values (Critical)
| Field | Missing | Percentage |
|-------|---------|------------|
| Close Date (A) | 318 | 91.9% |
| Closure Probability | 258 | 74.6% |
| **Masked Deal value** | **181** | **52.3%** |
| Tentative Close Date | 74 | 21.4% |
| Product deal | 170 | 49.1% |
| Sector/service | 8 | 2.3% |
| Owner code | 17 | 4.9% |

**Impact:** 52.3% of deals have no monetary value - these must be excluded from pipeline calculations.

#### Corrupt/Header Records
- 2 records contain "Deal Status" as value (header fragments)
- 2 records contain "Closure Probability" as value
- 2 records contain "Product deal" as value
- These need filtering during normalization

### Deal Status Distribution
```
Won:     165 (47.7%)
Dead:    127 (36.7%)
Open:     49 (14.2%)
On Hold:   2 (0.6%)
Invalid:   3 (header fragments)
```

### Deal Stage Analysis
```
A. Lead Generated:                      74
H. Work Order Received:                 46
L. Project Lost:                        42
E. Proposal/Commercials Sent:           28
G. Project Won:                         27
M. Projects On Hold:                    20
N. Not relevant at the moment:          19
Project Completed:                      19
O. Not Relevant at all:                 18
B. Sales Qualified Leads:               14
F. Negotiations:                        13
C. Demo Done:                            9
J. Invoice sent:                         6
D. Feasibility:                          4
I. POC:                                  3
K. Amount Accrued:                       2
```

### Sector Distribution
```
Renewables:                            111 (32.1%)
Mining:                                106 (30.6%)
Railways:                               40 (11.6%)
Others:                                 28 (8.1%)
Powerline:                              26 (7.5%)
Construction:                            9 (2.6%)
DSP:                                     7 (2.0%)
Tender:                                  5 (1.4%)
Manufacturing:                           2 (0.6%)
Security and Surveillance:               1 (0.3%)
Aviation:                                1 (0.3%)
Missing:                                 8 (2.3%)
```

**Key Sectors:** Renewables and Mining dominate (62.7% of deals).

### Financial Analysis (165 deals with values)
```
Total Pipeline:         ₹2,305,518,041 (~₹230.5 Cr)
Mean Deal Value:        ₹13,972,837
Median Deal Value:      ₹1,101,060
Min:                    ₹51,440
Max:                    ₹751,473,450
```

**Note:** High variance between mean and median indicates significant outliers.

### Closure Probability
```
High:     48
Medium:   22
Low:      16
Missing: 258 (74.6%)
```

**Weighted Pipeline Calculation:** With 74.6% missing probability, weighted pipeline requires assumptions.

### Owner Distribution
```
OWNER_003:    174 deals (50.3%)
OWNER_001:     88 deals (25.4%)
OWNER_002:     24 deals (6.9%)
OWNER_006:     24 deals (6.9%)
OWNER_004:     17 deals (4.9%)
OWNER_005:     11 deals (3.2%)
OWNER_007:      8 deals (2.3%)
```

### Date Fields
```
Close Date (A):           28 non-null (8.1%)  - Actual close dates
Tentative Close Date:    272 non-null (78.6%) - Expected close dates
Created Date:            345 non-null (99.7%) - Deal creation dates
```

**Quarterly Analysis:** Use Tentative Close Date for pipeline forecasting.

---

## 2. WORK ORDERS BOARD ANALYSIS

### Basic Statistics
- **Total Records:** 176
- **Columns:** 38
- **Purpose:** Project execution tracking

### Key Column Schema
```
Deal name masked                                    - Text (deal reference)
Customer Name Code                                  - Text (client code)
Serial #                                            - Text (WO identifier)
Nature of Work                                      - Text (project type)
Execution Status                                    - Status (Completed/Ongoing/etc.)
Sector                                              - Text (industry)
Billed Value in Rupees (Excl of GST.) (Masked)     - Number (INR)
Collected Amount in Rupees (Incl of GST.) (Masked) - Number (INR)
Amount Receivable (Masked)                          - Number (INR)
Date of PO/LOI                                      - Date
Probable Start Date                                 - Date
Probable End Date                                   - Date
```

### Data Quality Issues

#### Missing Values (Key Fields)
| Field | Missing | Percentage |
|-------|---------|------------|
| Collected Amount | 98 | 55.7% |
| **Billed Value** | **63** | **35.8%** |
| Nature of Work | 12 | 6.8% |
| Execution Status | 4 | 2.3% |
| Sector | 0 | 0.0% |
| Amount Receivable | 0 | 0.0% |

**Impact:** Financial calculations must handle significant nulls in billed/collected amounts.

### Sector Distribution
```
Mining:          100 (56.8%)
Renewables:       51 (29.0%)
Railways:         13 (7.4%)
Powerline:         6 (3.4%)
Others:            4 (2.3%)
Construction:      2 (1.1%)
```

**Comparison with Deals:** Mining has higher representation in operations (56.8%) vs sales (30.6%).

### Execution Status
```
Completed:                        117 (66.5%)
Ongoing:                           25 (14.2%)
Executed until current month:      12 (6.8%)
Not Started:                       11 (6.3%)
Pause / struck:                     4 (2.3%)
Partial Completed:                  2 (1.1%)
Details pending from Client:        1 (0.6%)
Missing:                            4 (2.3%)
```

### Nature of Work
```
One time Project:         125 (71.0%)
Proof of Concept:          15 (8.5%)
Annual Rate Contract:      14 (8.0%)
Monthly Contract:          10 (5.7%)
Missing:                   12 (6.8%)
```

### Financial Metrics (113 records with billed values)
```
Total Billed (Excl GST):     ₹107,389,777 (~₹10.7 Cr)
Total Collected (Incl GST):  ₹90,428,188 (~₹9.0 Cr)
Total Receivable:            ₹36,291,749 (~₹3.6 Cr)

Collection Rate:             84.2% (90.4M / 107.4M)
Outstanding:                 ₹3.6 Cr
```

**Insight:** Strong collection performance at 84.2%.

### Date Fields
```
Date of PO/LOI:           175 non-null (99.4%)
Probable Start Date:      158 non-null (89.8%)
Probable End Date:        157 non-null (89.2%)
Data Delivery Date:        58 non-null (33.0%)
```

---

## 3. CROSS-BOARD ANALYSIS

### Sector Overlap
**Deals Sectors (12 unique):**  
Renewables, Mining, Railways, Others, Powerline, Construction, DSP, Tender, Manufacturing, Security and Surveillance, Aviation

**Work Orders Sectors (6 unique):**  
Mining, Renewables, Railways, Powerline, Others, Construction

**Common Sectors (6):**  
Mining, Renewables, Railways, Powerline, Others, Construction

**Deals-Only Sectors:**  
DSP, Tender, Manufacturing, Security and Surveillance, Aviation

### Join Key Analysis

#### Deal Name Join
```
Deals unique 'Deal Name':                 155
Work Orders unique 'Deal name masked':     58
```

**Reliability:** LOW - Many-to-many relationships likely, inconsistent naming.

**Recommendation:** Do NOT force deal-level joins. Use **sector-level aggregation** for cross-board analysis.

### Sector-Level Comparison

| Sector | Deals Count | Deals Pipeline | WO Count | WO Billed |
|--------|-------------|----------------|----------|-----------|
| Mining | 106 (30.6%) | Data varies | 100 (56.8%) | Majority of billing |
| Renewables | 111 (32.1%) | Data varies | 51 (29.0%) | Significant billing |
| Railways | 40 (11.6%) | Data varies | 13 (7.4%) | Lower execution |
| Powerline | 26 (7.5%) | Data varies | 6 (3.4%) | Minimal execution |
| Others | 28 (8.1%) | Data varies | 4 (2.3%) | Minimal execution |
| Construction | 9 (2.6%) | Data varies | 2 (1.1%) | Minimal execution |

**Insight:** Mining dominates operations (56.8%) while Renewables leads sales (32.1%).

---

## 4. DATA NORMALIZATION REQUIREMENTS

### Text Normalization
```
Sectors:
  " Mining " → "Mining"
  "MINING" → "Mining"
  "mining" → "Mining"
  
Statuses:
  " Completed " → "Completed"
  "completed" → "Completed"
  
Deal Stages:
  Preserve exact values (complex hierarchy)
```

### Date Parsing
Multiple formats detected:
- ISO: "2026-02-26 00:00:00"
- DD/MM/YY
- DD-MM-YYYY

**Strategy:** Use flexible date parser with fallback.

### Numeric Cleaning
```
Deal values: Some stored as strings, need conversion
Financial fields: Mixed null/zero/empty
```

### Filtering Invalid Records
```
Remove records where:
  - Deal Name == "Deal Name" (header fragments)
  - Deal Status == "Deal Status" (header fragments)
  - Serial # == "Serial #" (header fragments)
```

---

## 5. METRIC DEFINITIONS

### Pipeline Metrics

#### Known Pipeline
```python
Sum of non-null 'Masked Deal value' 
WHERE Deal Status IN ('Open', 'Won')
  AND 'Masked Deal value' IS NOT NULL
  AND 'Masked Deal value' > 0
```

#### Weighted Pipeline
```python
Probability mapping:
  High: 0.7
  Medium: 0.5
  Low: 0.3
  NULL: 0.3 (conservative default)

Weighted Pipeline = Sum(Deal Value × Probability)
WHERE conditions same as Known Pipeline
```

#### Quarterly Pipeline
```python
Use 'Tentative Close Date' to filter by quarter
Current Quarter: Q3 2026 (Aug-Sep-Oct)
```

### Financial Metrics

#### Billed Value
```python
Sum of 'Billed Value in Rupees (Excl of GST.) (Masked)'
WHERE NOT NULL
```

#### Collected Amount
```python
Sum of 'Collected Amount in Rupees (Incl of GST.) (Masked)'
WHERE NOT NULL
```

#### Receivables
```python
Sum of 'Amount Receivable (Masked)'
WHERE NOT NULL
```

### Operations Metrics

#### Active Work Orders
```python
Count WHERE Execution Status IN ('Ongoing', 'Not Started')
```

#### Delayed Work Orders
```python
WHERE Execution Status IN ('Pause / struck', 'Details pending from Client')
   OR (Execution Status == 'Not Started' 
       AND Probable Start Date < TODAY)
```

---

## 6. DATA QUALITY FLAGS

### Critical Issues
- ❌ 52.3% of deals missing deal values
- ❌ 91.9% of deals missing actual close dates
- ❌ 74.6% of deals missing closure probability
- ❌ 35.8% of work orders missing billed values
- ❌ 55.7% of work orders missing collected amounts

### Warning Issues
- ⚠️ Deal-level joins unreliable
- ⚠️ Header fragment records present
- ⚠️ Inconsistent categorical values
- ⚠️ Mixed date formats

### Acceptable Issues
- ✓ Sector coverage good (0% missing in WO)
- ✓ Execution status mostly complete (2.3% missing)
- ✓ PO dates comprehensive (99.4% present)

---

## 7. RECOMMENDATIONS

### For Analytics
1. **Always exclude null deal values** from financial aggregations
2. **Use sector-level analysis** for cross-board queries
3. **Default to conservative probability** (0.3) when missing
4. **Clearly communicate exclusions** in results

### For Data Quality
1. **Transparent reporting** - Show missing value counts
2. **Caveat-driven responses** - Explain data limitations
3. **Provenance tracking** - Record what was included/excluded

### For Pipeline Calculations
1. Use **Tentative Close Date** for forecasting (78.6% coverage)
2. Filter by **Deal Status** ('Open', 'Won' for active pipeline)
3. **Exclude 181 deals** with no value from financial totals
4. **Report both Known and Weighted** pipeline

### For Cross-Board Analysis
1. **Sector-level aggregation** only
2. Do **NOT** assume 1:1 deal-to-WO mapping
3. Compare **relative performance** by sector
4. Explain that analysis is sector-level, not deal-level

---

## 8. CONCLUSION

The dataset requires robust data quality handling but contains sufficient information for meaningful business intelligence:

- **Pipeline analysis:** Viable with 165 valued deals
- **Financial analysis:** Viable with 113 billed work orders
- **Sector analysis:** Excellent coverage across both boards
- **Cross-board analysis:** Viable at sector level only

**Critical Success Factors:**
1. Dynamic normalization of messy data
2. Transparent communication of data quality issues
3. Appropriate handling of missing values
4. Sector-level (not deal-level) cross-board analysis

---

**Audit Complete:** Data is suitable for BI agent with appropriate quality handling.
