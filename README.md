# Council

A multi-agent decision-making system featuring diverse agent personalities that collaborate through persistent memory and structured deliberation cycles. Get balanced perspectives from different viewpoints before making decisions.

## Live Deployment

- Frontend: https://council-indol.vercel.app/

## Local Setup

### Prerequisites

Ensure you have installed:
- Python 3.8 or higher
- Node.js 16+ and npm
- Git

### Backend Setup

1. Navigate to the test directory:
```bash
cd test
```

2. Create a Python virtual environment:
```bash
python -m venv .venv
```

3. Activate the virtual environment:
```bash
# On Windows
.\.venv\Scripts\activate

# On macOS/Linux
source .venv/bin/activate
```

4. Install Python dependencies:
```bash
pip install python-dotenv
```

5. Configure environment variables. Create a `.env` file in the test directory with your LLM API credentials:
```bash
GROQ_API_KEY=your_groq_api_key_here
```

Or copy from template if available:
```bash
cp .env.example .env
# Then edit .env with your credentials
```

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install Node dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`

### Running the Complete System

There are two ways to interact with Council:

#### Option 1: CLI Mode (Interactive Terminal)

1. Ensure the backend `.env` is configured with your LLM credentials
2. In the `test` directory with `.venv` activated, start the agent council:
```bash
python main.py
```

3. Follow the prompts to select interaction mode and ask your question
4. The system will consult all agents and display their perspectives through multiple exchanges

#### Option 2: API Server + Frontend

The API server provides HTTP endpoints for the frontend UI to consume:

1. Start the API server in the `test` directory:
```bash
python api_server.py
```

The server runs on `http://localhost:8000`

**Available endpoints:**
- `GET /api/health` - Health check
- `POST /api/personalizer/questions` - Generate follow-up questions based on mode and query
- `POST /api/workflow` - Execute the full agent council workflow

2. In another terminal, start the frontend dev server from the `frontend` directory:
```bash
npm run dev
```

3. Open `http://localhost:5173` in your browser to interact with the UI

### Optional: Preserve Agent Memory

By default, agent memories reset at the start of each workflow run. To preserve memory across sessions:

```bash
export RESET_MEMORY_ON_START=0
# Then run either:
python main.py       # for CLI mode
# OR
python api_server.py # for API server
```

This applies to both CLI and API server modes. Set `RESET_MEMORY_ON_START=1` to reset memories on the next run.

---

## Deployment

### Quick Deploy to Vercel + Render (Free Tier)

This setup uses free hosting for both frontend and backend with zero infrastructure costs.

#### Prerequisites

- GitHub account with your Council repository
- Vercel account (free tier) at https://vercel.com
- Render account (free tier) at https://render.com
- OpenAI API key for LLM functionality

#### Step 1: Deploy Backend to Render

1. Go to https://render.com and sign in with GitHub
2. Click "New +" and select "Web Service"
3. Connect your Council repository
4. Configure the service:
    - Name: `council-api`
    - Root Directory: `test`
    - Build Command: (leave blank or `pip install python-dotenv`)
    - Start Command: `python api_server.py`
5. Add environment variable:
    - Key: `GROQ_API_KEY`
    - Value: Your Groq API key
6. Create Web Service (free tier, ~0.5GB RAM)
7. Wait for deployment and copy your service URL (e.g., `https://council-api.onrender.com`)

#### Step 2: Deploy Frontend to Vercel

1. Go to https://vercel.com and sign in with GitHub
2. Click "Add New..." and select "Project"
3. Import your Council repository
4. Configure the project:
    - Framework Preset: `Vite`
    - Root Directory: `./frontend`
    - Build Command: `npm run build`
    - Output Directory: `dist`
5. Add environment variable:
    - Key: `VITE_API_BASE_URL`
    - Value: Your Render backend URL (from Step 1, e.g., `https://council-api.onrender.com`)
6. Deploy
7. Once deployed, your frontend URL will be shown (current deployment: `https://council-indol.vercel.app/`)

#### Step 3: Access Your Deployment

- Frontend: Visit your Vercel URL
- API Health Check: Visit `https://council-api.onrender.com/api/health`

### Local Development with Environment Variables

For local development pointing to a deployed backend:

#### Backend (.env in `test/` directory)
```bash
GROQ_API_KEY=your_groq_api_key_here
```

#### Frontend (.env in `frontend/` directory)
```bash
VITE_API_BASE_URL=https://your-render-backend.onrender.com
```

Then run:
```bash
# Terminal 1: Backend
cd test
source .venv/bin/activate
python api_server.py

# Terminal 2: Frontend
cd frontend
npm run dev
```

### Persistent Agent Memory in Production

By default, agent memories persist across restarts within Render's filesystem. This means:
- Agent memories are preserved between API calls (single deployment)
- If the free-tier Render container restarts (happens after 15 minutes of inactivity), memories are retained
- To reset all memories on next deployment, set `RESET_MEMORY_ON_START=1` in Render environment variables


## Architecture

### System Overview

Council is a collaborative multi-agent system where diverse agent personalities work together to provide balanced decision-making support. The architecture consists of:

- **Frontend**: React-based UI for interaction
- **Backend**: Python multi-agent orchestration with persistent state
- **Agent Council**: 8 distinct personalities with independent memory
- **Personalizer**: Context-aware agent routing and questioning

### Agent Personalities

The council includes eight agents with complementary perspectives:

1. **Rational**: Logic-driven analysis with systematic reasoning
2. **Emotional**: Empathy-focused, intuition-based perspectives
3. **Conservative**: Risk-aware, preference for stability
4. **Ambitious**: Opportunity-seeker, growth-oriented views
5. **Optimist**: Positive framing, best-case scenario focus
6. **Pessimist**: Risks and challenges identification
7. **Realist**: Practical, evidence-based grounding
8. **What-If Ambitious**: Creative scenario exploration for "what if" mode

### Core Components

#### Personalizer (`personalizer/`)
Routes user queries to appropriate agents based on interaction mode:
- **Personal Consult**: Gathers context via follow-up questions, selects relevant agents
- **What If Scenario**: Creative exploration mode with speculative agents

#### Agent System (`agents/`)
Each agent inherits from `BaseAgent`:
- Maintains independent, persistent memory in JSON format
- Tracks conversation history and peer opinions
- Generates responses through LLM integration
- Participates in multi-exchange council deliberations

#### Memory (`memory/`)
Persistent state for each agent containing:
- Conversation history
- Exchange snapshots capturing peer interactions
- Opinion tracking (scores, sentiment, evolution)
- Self-state and last response

#### LLM Integration (`llm/`)
Unified interface to language model:
- Handles API calls with error recovery
- Separate pipelines for agent responses and personalizer routing
- Formats context and agent personality into prompts

### Multi-Exchange Deliberation Flow

1. **User Input**: Query and context gathered via personalizer
2. **Council Initialization**: Relevant agents loaded with their memories
3. **Exchanges (4 rounds)**:
   - Each agent responds to the query with full council context
   - Agents see previous round responses and adjust perspectives
   - Responses incorporated into shared deliberation history
4. **Memory Update**: Each agent's memory updated with exchange outcome
5. **Completion**: User receives comprehensive perspectives from all viewpoints

### Data Flow

```
User Input
    |
    v
[Personalizer] -> Gathers context, selects mode
    |
    v
[Agent Council] -> Load persistent memories
    |
    v
[Exchange Loop 1-4]:
    |
    +-> [Rational Agent] -> Generate response + Update memory
    |
    +-> [Emotional Agent] -> Generate response + Update memory
    |
    +-> [Conservative Agent] -> Generate response + Update memory
    ... (for all 8 agents)
    |
    v
[Output] -> Aggregated perspectives for user
```

### Persistence

- Agent memories stored in `memory/*.json` files
- Each agent maintains independent state between sessions
- Optional memory reset on startup (controlled by `RESET_MEMORY_ON_START`)
- No external database required - pure file-based persistence

---

## Project Structure

```
Council/
├── test/                          # Python backend
│   ├── main.py                   # CLI entry point
│   ├── api_server.py             # HTTP API server
│   ├── agents/                   # Agent implementations
│   │   ├── base_agent.py         # Base agent class
│   │   ├── rational.py           # Personality implementations
│   │   ├── emotional.py
│   │   ├── conservative.py
│   │   ├── ambitious.py
│   │   ├── optimist.py
│   │   ├── pessimist.py
│   │   ├── realist.py
│   │   ├── whatif_ambitious.py
│   │   └── loader.py             # Agent factory
│   ├── personalizer/             # User context gathering
│   │   └── personalizer.py       # Context and routing logic
│   ├── llm/                      # Language model integration
│   │   └── client.py             # LLM API calls
│   ├── memory/                   # Agent state persistence
│   │   ├── rational.json
│   │   ├── emotional.json
│   │   └── ... (one per agent)
│   ├── utils/                    # Shared utilities
│   │   └── helpers.py            # JSON/file helpers
│   └── .env                      # API credentials (local)
│
├── frontend/                       # React UI
│   ├── src/
│   │   ├── App.jsx               # Main application
│   │   ├── components/           # React components
│   │   ├── config/               # Configuration
│   │   └── index.css             # Styles with Tailwind
│   ├── package.json              # Node dependencies
│   ├── vite.config.js            # Build configuration
│   └── tailwind.config.js        # Tailwind setup
│
├── .gitignore                     # Git ignore rules
└── README.md                      # This file
```