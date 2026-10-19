# Skylark Drones - Monday.com Business Intelligence Agent

An AI-powered Business Intelligence agent that answers founder-level questions by dynamically querying Monday.com boards containing work orders and sales pipeline data.

## Overview

This agent enables executives to ask natural language questions about business performance and receive accurate, data-driven answers with full transparency about data quality and calculation methods.

**Example Questions:**
- "How's our pipeline looking for the energy sector this quarter?"
- "Which projects are delayed?"
- "How much have we billed and collected?"
- "Compare Mining and Renewables sectors"
- "Prepare a leadership update"

## Key Features

- **Live Monday.com Integration** - All data retrieved dynamically from Monday boards
- **Data Resilience** - Handles missing values, inconsistent formats, and messy real-world data
- **Deterministic Calculations** - All financial/numeric calculations done in Python, not LLM
- **Executive-Friendly** - Clear insights with data quality transparency
- **Cross-Board Analysis** - Analyzes relationships between deals and operations
- **Leadership Updates** - Automated executive briefing generation

## Architecture

```
User Browser
    ↓
Next.js Frontend (Vercel)
    ↓
FastAPI Backend (Render)
    ↓
AI Agent Orchestrator
    ↓
Controlled Tools
    ↓
Monday.com GraphQL API
```

### Core Principles

1. **Monday.com is Source of Truth** - No hardcoded data, all queries hit Monday live
2. **Read-Only Integration** - Agent never modifies Monday data
3. **Dynamic Normalization** - Data cleaned in-memory, never written back
4. **Deterministic Analytics** - Python handles all calculations
5. **LLM for Interpretation** - AI understands queries and explains results
6. **Security First** - All secrets remain server-side

## Project Structure

```
.
├── backend/                 # FastAPI backend
│   ├── api/                # API endpoints
│   ├── agent/              # AI agent orchestration
│   ├── monday/             # Monday.com client
│   ├── data/               # Normalization & quality
│   ├── analytics/          # BI calculations
│   └── tests/              # Test suite
├── frontend/               # Next.js frontend
│   ├── app/                # Pages (overview, ask, pipeline, etc.)
│   ├── components/         # React components
│   └── lib/                # API client
├── docs/                   # Documentation
│   ├── IMPLEMENTATION_PLAN.md
│   ├── ARCHITECTURE.md
│   ├── DECISION_LOG.md
│   ├── DATA_AUDIT.md
│   ├── BOARD_SCHEMA.md
│   └── METRIC_DEFINITIONS.md
└── README.md
```

## Setup

### Prerequisites

- Python 3.11+
- Node.js 18+
- Monday.com account with API access
- OpenAI or Anthropic API key

### Monday.com Setup

1. **Import Data to Monday.com:**
   - Create a new workspace
   - Import `Deal funnel Data.xlsx` as "Deals" board
   - Import `Work_Order_Tracker Data.xlsx` as "Work Orders" board
   - Set appropriate column types during import

2. **Generate API Token:**
   - Go to Monday.com → Profile → Admin → API
   - Generate a new API token with read-only scope
   - Copy the token and board IDs

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add:
# MONDAY_API_TOKEN=your_token
# MONDAY_DEALS_BOARD_ID=your_board_id
# MONDAY_WORK_ORDERS_BOARD_ID=your_board_id
# LLM_API_KEY=your_openai_or_anthropic_key

# Run backend
uvicorn main:app --reload --port 8000
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env.local
# Edit .env.local and add:
# NEXT_PUBLIC_API_URL=http://localhost:8000

# Run frontend
npm run dev
```

Visit http://localhost:3000

## Testing

```bash
# Backend tests
cd backend
pytest

# Run specific test categories
pytest tests/test_analytics.py      # Analytics calculations
pytest tests/test_normalizer.py     # Data normalization
pytest tests/test_monday.py         # Monday.com integration
pytest tests/test_agent.py          # Agent scenarios

# Critical: Live data test
pytest tests/test_live_monday.py    # Verifies dynamic Monday updates
```

## Deployment

### Backend (Render)

1. Create new Web Service on Render
2. Connect GitHub repository
3. Configure:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Add environment variables:
   - `MONDAY_API_TOKEN`
   - `MONDAY_DEALS_BOARD_ID`
   - `MONDAY_WORK_ORDERS_BOARD_ID`
   - `LLM_API_KEY`
   - `FRONTEND_URL` (after frontend deployment)
5. Deploy

### Frontend (Vercel)

1. Import repository to Vercel
2. Configure:
   - **Framework Preset:** Next.js
   - **Root Directory:** `frontend`
3. Add environment variable:
   - `NEXT_PUBLIC_API_URL=<render_backend_url>`
4. Deploy

## API Endpoints

```
GET  /health                        # Health check
POST /api/chat                      # Conversational queries
GET  /api/dashboard/overview        # Overview metrics
GET  /api/dashboard/pipeline        # Pipeline analysis
GET  /api/dashboard/operations      # Operations metrics
POST /api/leadership-update         # Generate leadership briefing
GET  /api/data-quality             # Data quality report
```

## Example Queries

**Pipeline Analysis:**
- "What is our current pipeline?"
- "How much pipeline do we have in Mining?"
- "Which sector has the strongest pipeline?"
- "What's our weighted pipeline this quarter?"

**Operations:**
- "Which projects are delayed?"
- "How many active work orders do we have?"
- "What's our execution status?"

**Financial:**
- "How much have we billed?"
- "How much have we collected?"
- "What's our outstanding receivables?"

**Cross-Board:**
- "Which sectors have strong pipeline but weak execution?"
- "Compare Mining and Renewables"

**Leadership:**
- "Prepare a leadership update"

## Data Quality Handling

The agent transparently communicates data quality issues:

- Missing values
- Invalid dates
- Inconsistent categories
- Duplicate records
- Unreliable relationships

Example response:
```
Known pipeline is ₹4.2Cr across 41 deals.

⚠ Data Quality:
- 7 deals are missing deal values (excluded from total)
- 3 opportunities missing expected close dates
```

## Limitations

- Read-only Monday.com access (no data modification)
- Cross-board joins limited to sector-level analysis
- Historical trend analysis not implemented
- Time-series forecasting not included
- No caching (always queries Monday live)

## Documentation

- **[IMPLEMENTATION_PLAN.md](docs/IMPLEMENTATION_PLAN.md)** - Detailed implementation plan
- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** - System architecture details
- **[DECISION_LOG.md](docs/DECISION_LOG.md)** - Key decisions and trade-offs
- **[DATA_AUDIT.md](docs/DATA_AUDIT.md)** - Data quality audit
- **[BOARD_SCHEMA.md](docs/BOARD_SCHEMA.md)** - Monday.com board schemas
- **[METRIC_DEFINITIONS.md](docs/METRIC_DEFINITIONS.md)** - Business metric definitions

## Security

- All secrets stored in environment variables
- No secrets in code or logs
- CORS properly configured
- Monday API token has read-only scope
- HTTPS enforced in production

## License

Proprietary - Skylark Drones Technical Assignment

## Contact

For questions about this submission, refer to the assignment documentation.
