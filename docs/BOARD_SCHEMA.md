# Monday.com Board Schemas

**Workspace:** My Team (3365327)  
**Base URL:** https://rvu470177.monday.com

---

## Deals Board

**Board ID:** `5030845871`  
**URL:** https://rvu470177.monday.com/boards/5030845871  
**Purpose:** Sales pipeline tracking

### Columns

| Column Name | Type | Required | Notes |
|-------------|------|----------|-------|
| Deal Name | Text | Yes | Primary identifier (155 unique) |
| Owner code | Text | No | BD/KAM personnel (7 unique owners) |
| Client Code | Text | No | Client identifier |
| Deal Status | Status | Yes | Won/Dead/Open/On Hold |
| Close Date (A) | Date | No | Actual close date (8.1% populated) |
| Closure Probability | Text | No | High/Medium/Low (25.4% populated) |
| Masked Deal value | Number | No | INR value (47.7% populated) |
| Tentative Close Date | Date | No | Expected close (78.6% populated) |
| Deal Stage | Status | Yes | A-O stages (17 unique stages) |
| Product deal | Text | No | Product mix description |
| Sector/service | Text | Yes | Industry sector (12 unique) |
| Created Date | Date | Yes | Deal creation timestamp |

### Key Statistics
- **Total Items:** ~346
- **Valued Deals:** 165 (47.7%)
- **Open Deals:** 49
- **Won Deals:** 165
- **Dead Deals:** 127

---

## Work Orders Board

**Board ID:** `5030845875`  
**URL:** https://rvu470177.monday.com/boards/5030845875  
**Purpose:** Project execution and billing tracking

### Columns

| Column Name | Type | Required | Notes |
|-------------|------|----------|-------|
| Deal name masked | Text | Yes | Deal reference |
| Customer Name Code | Text | Yes | Client code |
| Serial # | Text | Yes | WO unique identifier |
| Nature of Work | Text | No | Project type (One time/POC/Contract) |
| Last executed month of recurring project | Text | No | For recurring projects |
| Execution Status | Status | Yes | Completed/Ongoing/Not Started/etc. |
| Data Delivery Date | Date | No | Actual delivery date |
| Date of PO/LOI | Date | Yes | PO/LOI issuance date (99.4% populated) |
| Document Type | Text | Yes | Purchase Order/LOI/etc. |
| Probable Start Date | Date | No | Expected start |
| Probable End Date | Date | No | Expected end |
| BD/KAM Personnel code | Text | Yes | Account manager |
| Sector | Text | Yes | Industry sector (6 unique) |
| Type of Work | Text | Yes | Work description |
| Is any Skylark software platform part of the client deliverables in this deal? | Text | No | Platform usage flag |
| Last invoice date | Date | No | Most recent invoice |
| latest invoice no. | Text | No | Invoice number |
| Amount in Rupees (Excl of GST) (Masked) | Number | No | PO amount excluding GST |
| Amount in Rupees (Incl of GST) (Masked) | Number | No | PO amount including GST |
| Billed Value in Rupees (Excl of GST.) (Masked) | Number | No | Total billed (64.2% populated) |
| Billed Value in Rupees (Incl of GST.) (Masked) | Number | No | Total billed with GST |
| Collected Amount in Rupees (Incl of GST.) (Masked) | Number | No | Total collected (44.3% populated) |
| Amount to be billed in Rs. (Exl. of GST) (Masked) | Number | No | Pending billing amount |
| Amount to be billed in Rs. (Incl. of GST) (Masked) | Number | No | Pending billing with GST |
| Amount Receivable (Masked) | Number | Yes | Outstanding amount (100% populated) |
| AR Priority account | Text | No | Priority flag for collections |
| Quantity by Ops | Text | No | Operational quantity |
| Quantities as per PO | Text | No | Contractual quantity |
| Quantity billed (till date) | Number | No | Billed quantity |
| Balance in quantity | Text | No | Remaining quantity |
| Invoice Status | Text | No | Invoicing status |
| Expected Billing Month | Date | No | Planned billing period |
| Actual Billing Month | Date | No | Actual billing period |
| Actual Collection Month | Date | No | Collection period |
| WO Status (billed) | Text | No | Billing completion status |
| Collection status | Text | No | Collection completion status |
| Collection Date | Date | No | Collection timestamp |
| Billing Status | Text | Yes | Overall billing status |

### Key Statistics
- **Total Items:** ~176
- **Completed Projects:** 117 (66.5%)
- **Ongoing Projects:** 25 (14.2%)
- **Billed Projects:** 113 (64.2%)
- **Total Billed:** ₹10.7 Cr
- **Total Collected:** ₹9.0 Cr
- **Outstanding:** ₹3.6 Cr

---

## Monday.com API Access

### Authentication
```bash
Authorization: Bearer gsk_7CzuP51hqU5g2qCBGZa0WGdyb3FYXZn5eiIJ7i7HjJ3uJdvnfFEmllm
```

### GraphQL Endpoint
```
https://api.monday.com/v2
```

### Example Query
```graphql
query {
  boards(ids: [5030845871]) {
    id
    name
    columns {
      id
      title
      type
    }
    items_page(limit: 10) {
      cursor
      items {
        id
        name
        column_values {
          id
          text
          value
        }
      }
    }
  }
}
```

---

## Data Integrity Notes

1. **Deal Name vs Deal name masked:** Different fields, no guaranteed 1:1 mapping
2. **Sector alignment:** Work Orders uses subset of Deals sectors
3. **Financial fields:** Multiple null values, must handle gracefully
4. **Date formats:** Mixed formats in source data
5. **Header fragments:** Some records contain column names as values (need filtering)

---

## Query Patterns

### Get All Deals
```graphql
query {
  boards(ids: [5030845871]) {
    items_page(limit: 100) {
      cursor
      items {
        id
        name
        column_values {
          id
          title
          text
          value
        }
      }
    }
  }
}
```

### Get All Work Orders
```graphql
query {
  boards(ids: [5030845875]) {
    items_page(limit: 100) {
      cursor
      items {
        id
        name
        column_values {
          id
          title
          text
          value
        }
      }
    }
  }
}
```

### Pagination
Use `cursor` from response to fetch next page:
```graphql
query {
  next_items_page(limit: 100, cursor: "previous_cursor_value") {
    cursor
    items {
      ...
    }
  }
}
```

---

**Last Updated:** August 25, 2026
