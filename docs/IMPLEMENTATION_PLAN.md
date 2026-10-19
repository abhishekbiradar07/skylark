# Skylark Drones - Monday.com BI Agent Implementation Plan

**Date:** August 25, 2026  
**Project:** Monday.com Business Intelligence Agent  
**Timeline:** 6 hours  
**Status:** Initial Planning Phase

---

## 1. CURRENT PROJECT STATE

### Project Status
- **Starting State:** Empty repository
- **Phase:** Initial setup required
- **Documentation:** None exists yet
- **Code:** No existing codebase
- **Monday.com:** Boards need to be configured with provided data

### What Needs to be Created
1. Complete backend infrastructure
2. Monday.com integration layer
3. Data normalization and quality engine
4. Analytics calculation engine
5. AI agent orchestration
6. Frontend dashboard and chat interface
7. Documentation and deployment configuration

---

## 2. MONDAY.COM BOARD CONFIGURATION

### Required Setup
**Boards to Create:**
1. **Deals Board** - Import from `Deal funnel Data.xlsx`
2. **Work Orders Board** - Import from `Work_Order_Tracker Data.xlsx`

### Configuration Requirements
- Set appropriate column types during import
- Obtain board IDs after creation
- Generate Monday.com API token (read-only scope)
- Document actual board schemas after import

### Environment Variables Needed
```
MONDAY_API_TOKEN=<token>
MONDAY_DEALS_BOARD_ID=<board_id>
MONDAY_WORK_ORDERS_BOARD_ID=<board_id>
LLM_API_KEY=<openai_or_anthropic_key>
```

### Critical Constraints
- **READ ONLY** - Production agent must never write/update Monday data
- Must query Monday.com dynamically at runtime
- No hardcoded CSV/Excel data in application
- Must handle live data changes

---

## 3. PROPOSED ARCHITECTURE

### System Architecture
```
User (Browser)
    ↓
Frontend (Next.js on Vercel)
    ↓ HTTPS
Backend API (FastAPI on Render)
    ↓
AI Agent Orchestrator
    ↓
Controlled Tools Layer
    ↓
Monday.com Client (GraphQL)
    ↓
Monday.com API (Live Data)
```

### Data Flow
```
User Query
    ↓
Intent Understanding (LLM)
    ↓
Tool Selection & Planning
    ↓
Monday Data Retrieval (RAW)
    ↓
Dynamic Normalization (In-Memory)
    ↓
Data Quality Validation
    ↓
Deterministic BI Calculations (Python)
    ↓
Result Interpretation (LLM)
    ↓
Executive-Friendly Response
```

### Key Architectural Principles
1. **Monday as Source of Truth** - All runtime data from Monday.com
2. **Dynamic Normalization** - Clean data in-memory, never write back
3. **Deterministic Calculations** - Python handles all math/aggregations
4. **LLM for Interpretation** - AI understands queries and explains results
5. **Controlled Tools** - No direct data access for LLM
6. **Security First** - All secrets server-side

---

## 4. BACKEND PLAN

### Technology Stack
- **Framework:** FastAPI (Python 3.11+)
- **Data Processing:** Pandas for analytics
- **AI/LLM:** OpenAI or Anthropic with function calling
- **Monday Client:** Custom GraphQL client
- **Validation:** Pydantic models
- **Testing:** Pytest

### Directory Structure
```
backend/
├── main.py                 # FastAPI app entry
├── config/
│   ├── settings.py         # Environment config
│   └── logging.py          # Structured logging
├── api/
│   ├── chat.py             # Chat endpoint
│   ├── dashboard.py        # Dashboard data endpoints
│   └── health.py           # Health check
├── agent/
│   ├── orchestrator.py     # Main agent logic
│   ├── prompts.py          # System prompts
│   ├── tools.py            # Tool definitions
│   └── schemas.py          # Tool schemas
├── monday/
│   ├── client.py           # GraphQL client
│   ├── queries.py          # Query templates
│   ├── schemas.py          # Monday data models
│   └── mapper.py           # Raw → domain mapping
├── data/
│   ├── normalizer.py       # Dynamic cleaning
│   ├── validator.py        # Data validation
│   ├── quality.py          # Quality reporting
│   └── models.py           # Domain models
├── analytics/
│   ├── pipeline.py         # Pipeline calculations
│   ├── finance.py          # Financial metrics
│   ├── operations.py       # Operations metrics
│   └── cross_board.py      # Cross-board analysis
└── tests/
    ├── test_monday.py
    ├── test_normalizer.py
    ├── test_analytics.py
    └── test_agent.py
```

### API Endpoints
```
GET  /health
POST /api/chat
GET  /api/dashboard/overview
GET  /api/dashboard/pipeline
GET  /api/dashboard/operations
POST /api/leadership-update
GET  /api/data-quality
```

---

## 5. DYNAMIC NORMALIZATION PLAN

### Normalization Strategy
**CRITICAL:** Normalize dynamically after retrieval, never write back to Monday

### Raw vs Normalized Data Model
```python
# Raw layer - preserve Monday response
{
    "raw_sector": " energy ",
    "raw_value": "",
    "raw_close_date": "01/08/26"
}

# Normalized layer - in-memory only
{
    "sector": "Energy",
    "sector_normalized": "Energy",
    "value": None,
    "close_date": datetime(2026, 8, 1),
    "quality_flags": ["MISSING_DEAL_VALUE"]
}
```

### Normalization Functions
```python
normalize_text(value: str) -> str
normalize_sector(value: str) -> str
normalize_status(value: str) -> str
normalize_stage(value: str) -> str
normalize_date(value: str) -> datetime | None
normalize_currency(value: str) -> Decimal | None
normalize_number(value: str) -> float | None
```

### Normalization Rules (Data-Driven)
- Trim whitespace
- Consistent casing (Title Case for categories)
- Parse date formats (DD/MM/YY, DD-MM-YYYY, etc.)
- Convert numeric strings to proper types
- Canonicalize equivalent labels (e.g., "In Progress" = "In progress")
- **Never convert NULL to zero**
- **Flag ambiguous values, don't guess**

### Quality Flags
- `MISSING_VALUE`
- `INVALID_DATE`
- `MALFORMED_NUMBER`
- `INCONSISTENT_CATEGORY`
- `DUPLICATE_RECORD`
- `UNRELIABLE_JOIN`

---

## 6. ANALYTICS PLAN

### Deterministic Calculation Engine
**CRITICAL:** All financial/numeric calculations done in Python, not LLM

### Pipeline Metrics
```python
def calculate_pipeline(deals: List[Deal]) -> PipelineMetrics:
    """
    Known Pipeline: Sum of valid non-null deal values
    Weighted Pipeline: Sum of (deal_value * probability)
    Deal Count: Count of qualifying deals
    """
    
def calculate_pipeline_by_sector(deals: List[Deal]) -> Dict[str, PipelineMetrics]

def calculate_pipeline_by_stage(deals: List[Deal]) -> Dict[str, PipelineMetrics]

def calculate_expected_closes(deals: List[Deal], period: DateRange) -> PipelineMetrics
```

### Financial Metrics
```python
def calculate_billed_value(work_orders: List[WorkOrder]) -> Decimal

def calculate_collected_amount(work_orders: List[WorkOrder]) -> Decimal

def calculate_receivables(work_orders: List[WorkOrder]) -> Decimal

def calculate_to_be_billed(work_orders: List[WorkOrder]) -> Decimal
```

### Operations Metrics
```python
def calculate_active_work_orders(wos: List[WorkOrder]) -> int

def calculate_delayed_work_orders(wos: List[WorkOrder]) -> List[WorkOrder]

def calculate_execution_status(wos: List[WorkOrder]) -> ExecutionMetrics
```

### Cross-Board Analysis
```python
def analyze_sector_performance(
    deals: List[Deal],
    work_orders: List[WorkOrder]
) -> Dict[str, SectorAnalysis]:
    """
    Compare pipeline vs execution by SECTOR only.
    Do NOT force unreliable deal-level joins.
    """
```

### Metric Definitions Document
Create `docs/METRIC_DEFINITIONS.md` defining:
- What each metric means
- Inclusion/exclusion criteria
- Handling of nulls
- Calculation formula
- Data quality requirements

---

## 7. AGENT / TOOL PLAN

### LLM Orchestration
- **Provider:** OpenAI (GPT-4) or Anthropic (Claude)
- **Approach:** Function/tool calling
- **Role:** Query understanding + result interpretation
- **NOT:** Raw calculation or data manipulation

### Agent Tools (Controlled Functions)
```python
# Data retrieval
get_deals(filters: DealFilters) -> List[Deal]
get_work_orders(filters: WorkOrderFilters) -> List[WorkOrder]

# Analytics
calculate_pipeline(period: str, sector: str | None) -> PipelineResult
calculate_weighted_pipeline(period: str, sector: str | None) -> PipelineResult
analyze_sector(sector: str) -> SectorAnalysis
calculate_financial_metrics() -> FinancialMetrics
calculate_operations_metrics() -> OperationsMetrics

# Cross-board
compare_sectors(sector1: str, sector2: str) -> ComparisonResult
cross_board_analysis(dimension: str) -> CrossBoardResult

# Quality
get_data_quality_report() -> DataQualityReport

# Leadership
prepare_leadership_update() -> LeadershipUpdate
```

### Query Understanding
- Parse time periods (this quarter, Q1 2026, etc.)
- Extract entities (sectors, stages, owners)
- Identify intent (pipeline, operations, financial, comparison)
- Detect ambiguity and ask clarification

### Response Generation
- Executive-friendly language
- KPI cards with numbers
- Key insights (LLM interpretation)
- Data quality caveats
- Follow-up suggestions

---

## 8. FRONTEND PLAN

### Technology Stack
- **Framework:** Next.js 14 (App Router)
- **Language:** TypeScript
- **Styling:** Tailwind CSS
- **Components:** shadcn/ui
- **Charts:** Recharts or Chart.js
- **State:** React hooks (minimal state management)

### Pages/Routes
```
/                          # Overview dashboard
/ask                       # Conversational agent
/pipeline                  # Pipeline analysis
/operations                # Operations dashboard
/leadership                # Leadership briefing
```

### Overview Dashboard (`/`)
**Components:**
- KPI cards (Pipeline, Deal Count, Active Work Orders, etc.)
- Pipeline by sector (bar chart)
- Pipeline by stage (pie chart)
- Operations summary
- Data quality alerts
- Quick ask input

### Ask Agent Page (`/ask`)
**Components:**
- Chat interface (conversation history)
- Message input with suggested questions
- Rich response rendering (metrics, charts, insights)
- Data quality warnings
- Follow-up context maintenance

### Pipeline Page (`/pipeline`)
**Components:**
- Total/weighted pipeline cards
- Pipeline breakdown by sector
- Pipeline breakdown by stage
- Expected closes timeline
- Top opportunities table
- Filters (sector, stage, period)

### Operations Page (`/operations`)
**Components:**
- Active work orders count
- Completed work orders
- Delayed projects
- Billing status
- Collection status
- Operations by sector

### Leadership Page (`/leadership`)
**Components:**
- Executive summary
- Key metrics snapshot
- Pipeline highlights
- Operations highlights
- Financial highlights
- Risks and opportunities
- Data quality summary
- "Generate Update" button

### Design Language
- **Style:** Premium, modern, professional executive dashboard
- **Colors:** Neutral palette with strategic accent colors
- **Typography:** Clean, readable fonts
- **Layout:** Card-based, responsive
- **No:** Generic chatbot styling, excessive animations, cartoon AI imagery

---

## 9. TESTING PLAN

### Unit Tests
```python
# Data normalization
test_normalize_text()
test_normalize_sector()
test_normalize_date()
test_normalize_currency()
test_handle_null_values()
test_handle_malformed_values()

# Analytics
test_pipeline_calculation()
test_weighted_pipeline()
test_sector_aggregation()
test_date_filtering()
test_financial_metrics()
test_operations_metrics()

# Data quality
test_detect_missing_values()
test_detect_duplicates()
test_detect_invalid_dates()
```

### Integration Tests
```python
test_monday_client_connection()
test_monday_pagination()
test_monday_api_failure()
test_monday_authentication_error()
test_retrieve_deals_board()
test_retrieve_work_orders_board()
```

### Agent Tests (E2E Scenarios)
```python
test_query_overall_pipeline()
test_query_sector_pipeline("Mining")
test_query_unknown_sector("Energy")  # Should NOT hallucinate
test_query_quarterly_pipeline()
test_query_delayed_work_orders()
test_query_financial_metrics()
test_query_cross_board_analysis()
test_query_leadership_update()
test_query_with_missing_data()
```

### Critical Live Data Test
```python
def test_live_monday_updates():
    """
    1. Query a known deal value
    2. Manually change value in Monday.com
    3. Query again
    4. Assert new value is returned
    
    This proves dynamic Monday integration.
    """
```

### Data Resilience Tests
```python
test_handle_null_deal_value()
test_handle_invalid_date()
test_handle_inconsistent_sector()
test_handle_duplicate_records()
test_handle_missing_required_fields()
```

---

## 10. DEPLOYMENT PLAN

### Hosting Architecture
```
Frontend: Vercel (Next.js)
    ↓ HTTPS
Backend: Render (FastAPI)
    ↓ GraphQL
Monday.com API
```

### Environment Configuration
**Backend (Render):**
```bash
MONDAY_API_TOKEN=<secret>
MONDAY_DEALS_BOARD_ID=<board_id>
MONDAY_WORK_ORDERS_BOARD_ID=<board_id>
LLM_API_KEY=<openai_key>
FRONTEND_URL=https://<app>.vercel.app
LOG_LEVEL=INFO
```

**Frontend (Vercel):**
```bash
NEXT_PUBLIC_API_URL=https://<app>.onrender.com
```

### Security Checklist
- [ ] All secrets in environment variables
- [ ] No secrets committed to git
- [ ] .env in .gitignore
- [ ] .env.example provided
- [ ] CORS configured correctly
- [ ] No secrets exposed to frontend
- [ ] No secrets in logs
- [ ] API token has read-only scope
- [ ] HTTPS enforced

### Deployment Steps
1. Create Monday.com boards and obtain IDs
2. Generate Monday API token (read-only)
3. Set up backend on Render with environment variables
4. Deploy backend and verify health endpoint
5. Set up frontend on Vercel with API URL
6. Deploy frontend
7. Test end-to-end with live Monday data
8. Run evaluator scenarios
9. Document deployment URLs

---

## 11. RISKS & MITIGATION

### Risk: Monday API Rate Limiting
**Mitigation:** 
- Implement exponential backoff retry
- Use targeted queries where possible
- Monitor API usage

### Risk: Incomplete Monday Data
**Mitigation:**
- Comprehensive data quality validation
- Clear communication of missing data
- Graceful degradation

### Risk: Unreliable Cross-Board Joins
**Mitigation:**
- Use sector-level analysis instead
- Document join limitations
- Never force unreliable relationships

### Risk: LLM Hallucination
**Mitigation:**
- All calculations in Python, not LLM
- Structured tool outputs
- Validate LLM responses against actual data
- Clear provenance tracking

### Risk: Excel vs Monday Confusion
**Mitigation:**
- Clear documentation
- Live data test in test suite
- No Excel reading code in production path

### Risk: Time Constraint (6 hours)
**Mitigation:**
- MVP-first approach
- Core features prioritized
- Defer nice-to-haves
- Simple but correct over complex

---

## 12. IMPLEMENTATION ORDER

### Phase 1: Foundation (30 min)
- [ ] Create project structure
- [ ] Set up Python environment
- [ ] Install dependencies (FastAPI, Pydantic, Pandas, httpx)
- [ ] Create Next.js frontend skeleton
- [ ] Set up .env.example files

### Phase 2: Monday Integration (45 min)
- [ ] Import data to Monday.com boards
- [ ] Document actual board schemas
- [ ] Implement Monday GraphQL client
- [ ] Test connection and data retrieval
- [ ] Implement pagination
- [ ] Create domain models

### Phase 3: Data Layer (45 min)
- [ ] Implement normalization engine
- [ ] Implement data quality validator
- [ ] Create raw → normalized mapping
- [ ] Write data layer tests
- [ ] Document normalization rules

### Phase 4: Analytics Engine (60 min)
- [ ] Implement pipeline calculations
- [ ] Implement financial metrics
- [ ] Implement operations metrics
- [ ] Implement cross-board analysis
- [ ] Write analytics tests
- [ ] Document metric definitions

### Phase 5: AI Agent (45 min)
- [ ] Implement tool definitions
- [ ] Implement LLM orchestrator
- [ ] Create system prompts
- [ ] Test query understanding
- [ ] Test tool execution flow
- [ ] Handle edge cases (unknown entities, etc.)

### Phase 6: Backend API (30 min)
- [ ] Implement chat endpoint
- [ ] Implement dashboard endpoints
- [ ] Implement leadership update endpoint
- [ ] Add error handling
- [ ] Add logging
- [ ] Test API endpoints

### Phase 7: Frontend (90 min)
- [ ] Implement overview dashboard
- [ ] Implement ask agent page
- [ ] Implement pipeline page
- [ ] Implement operations page
- [ ] Implement leadership page
- [ ] Implement data quality UI
- [ ] Style and polish

### Phase 8: Integration & Testing (30 min)
- [ ] Connect frontend to backend
- [ ] Run E2E evaluator scenarios
- [ ] Run live data update test
- [ ] Fix critical issues
- [ ] Verify data quality warnings

### Phase 9: Deployment (30 min)
- [ ] Deploy backend to Render
- [ ] Deploy frontend to Vercel
- [ ] Configure environment variables
- [ ] Test production deployment
- [ ] Verify CORS and connectivity

### Phase 10: Documentation (30 min)
- [ ] Complete README.md
- [ ] Write ARCHITECTURE.md
- [ ] Write DECISION_LOG.md
- [ ] Write METRIC_DEFINITIONS.md
- [ ] Document API endpoints
- [ ] Prepare submission package

**Total Estimated: 6 hours**

---

## 13. DECISION LOG PREVIEW

### Key Decisions to Document

**1. Technology Choices**
- Why FastAPI + Next.js
- Why not vector DB or RAG
- Why structured tools over raw prompting

**2. Dynamic Normalization Strategy**
- Why normalize in-memory vs. persistent
- Why preserve raw values
- How to handle ambiguous values

**3. Cross-Board Analysis Approach**
- Why sector-level instead of deal-level joins
- Evidence for relationship reliability
- How to communicate limitations

**4. Leadership Update Interpretation**
- What "prepare for leadership updates" means
- What sections to include
- How to balance detail vs. brevity

**5. Trade-offs**
- Correctness vs. optimization
- Simplicity vs. features
- Data quality transparency vs. clean UX

**6. What Would Be Improved With More Time**
- More sophisticated time-series analysis
- Predictive analytics
- Drill-down capabilities
- More visualization options
- Caching strategy
- More comprehensive testing

---

## 14. SUCCESS CRITERIA

### Must Pass
- [ ] Agent answers "What is our current pipeline?" correctly
- [ ] Agent handles "How much pipeline in Mining?" correctly
- [ ] Agent handles unknown sector ("Energy") without hallucination
- [ ] Agent calculates quarterly pipeline correctly
- [ ] Agent identifies delayed work orders correctly
- [ ] Agent calculates financial metrics correctly
- [ ] Agent performs cross-board analysis correctly
- [ ] Agent generates leadership update
- [ ] Live data test: Monday changes reflected immediately
- [ ] No Excel files used at runtime
- [ ] All secrets server-side
- [ ] Data quality issues communicated

### Quality Indicators
- [ ] Executive-friendly responses
- [ ] Clear data provenance
- [ ] Appropriate clarifying questions
- [ ] Deterministic calculations
- [ ] Comprehensive error handling
- [ ] Professional UI design
- [ ] Complete documentation

---

## 15. NEXT STEPS

### Immediate Actions Required
1. **Obtain Monday.com credentials**
   - Create Monday.com account if needed
   - Generate API token (read-only scope)

2. **Import data to Monday.com**
   - Import `Deal funnel Data.xlsx` → Deals board
   - Import `Work_Order_Tracker Data.xlsx` → Work Orders board
   - Document board IDs

3. **Create data audit**
   - Inspect imported boards
   - Document actual schemas
   - Identify data quality issues
   - Create `docs/DATA_AUDIT.md`
   - Create `docs/BOARD_SCHEMA.md`
   - Create `docs/MONDAY_IMPORT_REPORT.md`

4. **Begin implementation**
   - Follow phase-by-phase plan above
   - Test continuously
   - Document decisions

### Questions for Clarification
- Do we have Monday.com account credentials?
- Have the Excel files been provided?
- What LLM provider should be used (OpenAI vs Anthropic)?
- Any specific deployment platform preferences?

---

**APPROVAL REQUIRED BEFORE PROCEEDING WITH IMPLEMENTATION**

This plan provides a comprehensive blueprint for building the Monday.com BI Agent according to all specified requirements. The implementation follows a phased approach prioritizing correctness, live Monday integration, data resilience, and executive-friendly UX.
