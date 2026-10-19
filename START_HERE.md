# 🚀 Skylark Drones BI Agent - Quick Start

## 📋 Prerequisites

1. **Python 3.8+** installed
2. **Node.js 18+** and npm installed
3. **Monday.com API token** (configured in `.env`)
4. **Groq API key** (configured in `.env`)

## 🏃 Quick Start (5 minutes)

### Step 1: Install Backend Dependencies

```bash
cd backend
pip install -r requirements.txt
cd ..
```

### Step 2: Configure Environment

The `.env` file is already configured with:
- ✅ Monday.com API token
- ✅ Board IDs (Deals: 5030845871, Work Orders: 5030845875)
- ✅ Groq API key
- ✅ Model: openai/gpt-oss-120b

### Step 3: Start Backend Server

```bash
python backend/main.py
```

Backend will start on http://localhost:8000

### Step 4: Test the System

Open a new terminal and run:

```bash
python test_full_system.py
```

This will test the AI agent with sample queries.

### Step 5: Start Frontend (Option A - Simple HTML)

Open `app/index.html` in your browser. It's a fully working standalone dashboard.

### Step 6: Start Frontend (Option B - Next.js)

```bash
cd frontend-app
npm install
npm run dev
```

Frontend will start on http://localhost:3000

## 🎯 Features Available

### ✅ Backend API (Port 8000)
- `/health` - Health check
- `/api/chat` - AI agent chat endpoint
- Monday.com integration
- Analytics engines (pipeline, finance, operations)

### ✅ AI Agent
- Natural language queries
- Tool execution (pipeline, financials, operations)
- Data quality reporting
- Cross-board sector analysis

### ✅ Frontend Dashboard
- **Overview**: Key metrics and insights
- **Ask Agent**: Chat interface for BI queries
- **Pipeline**: Sales pipeline analysis
- **Operations**: Project execution tracking
- **Financial**: Billing and collections

## 📊 Sample Queries

Try asking the agent:
- "What is our current pipeline?"
- "How much pipeline do we have in Mining?"
- "Which projects are delayed?"
- "Compare Mining and Renewables sectors"
- "What's our collection rate?"

## 🧪 Testing

### Test with Demo Data (No API calls)
```bash
python demo_simple.py
```

### Test Full System with Live Data
```bash
python test_full_system.py
```

### Test Backend Only
```bash
curl http://localhost:8000/health
```

### Test Agent Chat
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is our current pipeline?"}'
```

## 📁 Project Structure

```
skylark-bi-agent/
├── backend/              # FastAPI backend
│   ├── agent/           # AI agent (LLM + tools)
│   ├── analytics/       # Analytics engines
│   ├── config/          # Settings & logging
│   ├── data/            # Data models & processing
│   ├── monday/          # Monday.com client
│   └── main.py          # FastAPI app
├── frontend-app/        # Next.js frontend (Databricks theme)
│   ├── app/             # Next.js pages
│   └── components/      # React components
├── app/                 # Standalone HTML frontend
│   └── index.html       # Single-page dashboard
├── docs/                # Documentation
└── .env                 # Environment config
```

## 🔧 Troubleshooting

### Backend won't start
- Check Python version: `python --version` (need 3.8+)
- Install dependencies: `pip install -r backend/requirements.txt`
- Check if port 8000 is available

### Frontend won't connect
- Make sure backend is running on port 8000
- Check browser console for errors
- Update CORS settings in `backend/main.py` if needed

### Agent returns errors
- Verify Groq API key in `.env`
- Check backend logs for details
- Ensure Monday.com API token is valid

### No data showing
- Verify Monday.com board IDs in `.env`
- Check API token permissions
- Review Monday.com GraphQL queries in `backend/monday/queries.py`

## 📚 Documentation

- **Implementation Plan**: `docs/IMPLEMENTATION_PLAN.md`
- **Data Audit**: `docs/DATA_AUDIT.md`
- **Board Schema**: `docs/BOARD_SCHEMA.md`
- **Project Status**: `PROJECT_STATUS.txt`

## 🎓 Architecture

```
Monday.com (Live Data)
    ↓
Monday Client (GraphQL)
    ↓
Data Processing (Normalize, Validate)
    ↓
Analytics Engines (Deterministic calculations)
    ↓
AI Agent (LLM + Tools)
    ↓
FastAPI Backend
    ↓
Frontend Dashboard
```

## ✨ Key Features

- ✅ **Read-only** Monday.com integration
- ✅ **Dynamic normalization** (in-memory, never writes back)
- ✅ **Deterministic analytics** (Python, not LLM guessing)
- ✅ **Transparent data quality** reporting
- ✅ **Sector-level analysis** (no unreliable joins)
- ✅ **Natural language** queries via AI agent
- ✅ **Databricks-themed** modern UI

## 🚀 Deployment Ready

### Backend (Render/Railway)
```bash
# Backend runs on any Python 3.8+ environment
python backend/main.py
```

### Frontend (Vercel/Netlify)
```bash
cd frontend-app
npm run build
# Deploy .next folder
```

## 📞 Support

For issues or questions, refer to:
- Project documentation in `docs/`
- `PROJECT_STATUS.txt` for current status
- Code comments and docstrings

---

**Built for Skylark Drones Assignment - Monday.com Business Intelligence Agent**
