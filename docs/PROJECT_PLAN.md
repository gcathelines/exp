# BI Chat CLI - Project Documentation

## Project Overview
**Purpose**: Business Intelligence Chat CLI for internal developers and business analysts
**Goal**: Enable non-technical users to gather insights from BigQuery data without SQL knowledge
**Timeline**: 2 days
**Team**: 2 Claude Code agents + 1 reviewer developer

## Technical Stack
- **Language**: Python 3.11+
- **Package Manager**: uv (mandatory)
- **Agent Framework**: CrewAI (latest)
- **LLM Provider**: Google VertexAI with Google GenAI client (gemini-2.0-flash)
- **Data Source**: Google BigQuery (data-314708.intermediate_transaction.user_transaction)
- **CLI Framework**: Click/Typer with interactive slash commands
- **Visualization**: Plotly/Matplotlib
- **Session Management**: SQLite for persistent chat sessions
- **Knowledge Base**: ChromaDB for user_transaction context
- **Caching**: Redis for processed insights (>2s queries)
- **Safety**: Date filtering (≤30 days) and query validation
- **Auth**: Service account (/etc/creds/credentials_ai.json)

## Enhanced System Architecture

```
User Input → Session Manager → Interactive CLI → Knowledge Base Query → 
CrewAI Agents → Date Validator (≤30 days) → Cache Check → 
BigQuery → Safety Validation → Response + Confidence → 
Session Storage → Observability Log → User
```

### Components:
1. **Interactive CLI** (Agent 1)
   ├── Slash commands (/sessions, /new, /switch)
   ├── Session management (SQLite)
   ├── Date validation and safety
   └── BigQuery client integration

2. **Enhanced CrewAI Agent System** (Agent 2)
   ├── Query Agent: NL → SQL with date constraints
   ├── Analysis Agent: Data processing with caching
   ├── Visualization Agent: Charts & summaries
   └── Safety Agent: Query validation (≤30 days)

3. **Knowledge & Caching Layer** (Phase 2)
   ├── ChromaDB: user_transaction context
   ├── Redis: Processed insights cache
   └── Observability: Agent decision logging

4. **Safety & Reliability**
   ├── Automatic date filtering (≤30 days)
   ├── SQL injection prevention  
   ├── Confidence scoring
   └── Query cost awareness

## Project Structure

```
bi-chat-cli/
├── src/
│   ├── cli/                    # Agent 1: Interactive CLI with slash commands
│   │   ├── __init__.py
│   │   ├── main.py            # CLI entry point
│   │   ├── commands.py        # Slash command handlers
│   │   └── interactive.py     # Interactive session management
│   ├── sessions/              # Agent 1: Session management
│   │   ├── __init__.py
│   │   ├── manager.py         # SQLite session operations
│   │   ├── models.py          # Session data models
│   │   └── storage.py         # Persistent storage layer
│   ├── safety/                # Agent 1: Query validation & safety
│   │   ├── __init__.py
│   │   ├── date_validator.py  # Date range enforcement (≤30 days)
│   │   ├── sql_validator.py   # SQL injection prevention
│   │   └── query_limits.py    # Safety constraints
│   ├── data/                  # Agent 1: BigQuery integration
│   │   ├── __init__.py
│   │   ├── bigquery_client.py # BigQuery connection
│   │   ├── schema_discovery.py # Table/schema introspection
│   │   └── query_executor.py  # Query execution
│   ├── agents/                # Agent 2: CrewAI agent system
│   │   ├── __init__.py
│   │   ├── crew_setup.py      # CrewAI configuration
│   │   ├── query_agent.py     # NL → SQL with date constraints
│   │   ├── analysis_agent.py  # Data processing & insights
│   │   └── viz_agent.py       # Visualization generation
│   ├── output/                # Agent 2: Response formatting & visualization
│   │   ├── __init__.py
│   │   ├── formatters.py      # Response formatting
│   │   ├── visualizations.py  # Chart generation (Plotly/Matplotlib)
│   │   └── exporters.py       # Export utilities
│   ├── knowledge/             # Phase 2: ChromaDB knowledge base
│   │   ├── __init__.py
│   │   ├── embeddings.py      # Vector embeddings
│   │   ├── context_manager.py # Business context storage
│   │   └── similarity.py      # Query similarity matching
│   ├── cache/                 # Phase 2: Redis caching system
│   │   ├── __init__.py
│   │   ├── redis_client.py    # Redis connection
│   │   ├── insights_cache.py  # Processed insights cache
│   │   └── query_cache.py     # Query result caching
│   └── utils/                 # Shared utilities
│       ├── __init__.py
│       ├── config.py          # Configuration management
│       ├── observability.py   # Agent decision logging
│       └── token_tracker.py   # Token usage tracking
├── tests/
│   ├── unit/                  # Unit tests by component
│   │   ├── cli/, sessions/, safety/, data/
│   │   ├── agents/, output/, knowledge/, cache/
│   ├── integration/           # Integration tests
│   └── fixtures/              # Test data & mocks
├── docs/                      # Project documentation
│   ├── PROJECT_PLAN.md
│   ├── MULTI_AGENT_WORKFLOW.md
│   └── CLAUDE_CODE_SETUP.md
├── config/                    # Configuration files
├── CLAUDE.md                  # Claude Code memory
├── pyproject.toml            # uv package management
├── Dockerfile                # Container configuration
├── docker-compose.yml        # Development environment
├── README.md
└── .env.example              # Environment template
```

## Agent Assignments

### Agent 1 (User Interface + Core Safety)
**Responsibility**: Interactive CLI + Sessions + Safety + BigQuery
**Branches**: 
- `feature/cli-interface`
- `feature/sessions` 
- `feature/safety`

**MVP Tasks (Phase 1)**:
- Interactive CLI with slash commands (/sessions, /new, /switch)
- Session management using SQLite (multiple chat windows)
- Date validation and query safety (≤30 days)
- BigQuery client implementation
- Service account authentication

**Component Focus**:
- `src/cli/` - Interactive CLI system
- `src/sessions/` - SQLite session management
- `src/safety/` - Date & query validation
- `src/data/` - BigQuery integration

### Agent 2 (AI Core + Output System)
**Responsibility**: CrewAI Agents + Visualization + Response Formatting
**Branches**: 
- `feature/crew-agents`
- `feature/output-system`

**MVP Tasks (Phase 1)**:
- CrewAI agent configuration with gemini-2.0-flash
- Query generation agent (NL → SQL with date constraints)
- Data analysis agent with basic insights
- Visualization system (Plotly/Matplotlib)
- Response formatting and presentation

**Component Focus**:
- `src/agents/` - CrewAI agent system
- `src/output/` - Visualization & formatting

### Phase 2 Enhancements (Both Agents)
**Shared Post-MVP Tasks**:
- Knowledge base implementation (ChromaDB) - `src/knowledge/`
- Processed insights caching (Redis) - `src/cache/` 
- Enhanced observability logging - `src/utils/observability.py`
- Advanced safety and confidence scoring

### Reviewer Developer
**Responsibility**: Integration, Testing, Code Review
**Tasks**:
- Code review for all PRs
- Integration testing
- Dependency management
- Final integration and testing
- Documentation review

## Interface Contracts

```python
# Shared data models for integration
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

class QueryResult(BaseModel):
    data: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    execution_time: float
    row_count: int
    
class TokenUsage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    cost_estimate: float

class AgentResponse(BaseModel):
    content: str
    visualizations: Optional[List[Dict]]
    token_usage: TokenUsage
    timestamp: datetime
    
class UserQuery(BaseModel):
    query: str
    user_id: str
    session_id: str
    context: Optional[Dict[str, Any]] = None
```

## Development Standards

### Code Quality
- Python 3.11+ with type hints everywhere
- Black for code formatting
- Flake8 for linting
- Pydantic for data validation
- Pytest for testing (target >90% coverage)
- Comprehensive docstrings for all public functions

### Git Workflow
- Conventional commits: `feat:`, `fix:`, `docs:`, `test:`, `refactor:`
- No direct commits to main branch
- Pull request templates with checklists
- Rebase workflow for clean commit history
- Branch naming: `feature/`, `fix/`, `docs/`

### Testing Strategy
- Unit tests for individual components
- Integration tests for agent workflows
- Mock BigQuery responses for testing
- Fixture-based test data management
- Continuous integration checks

## MVP Features
1. **Core Functionality**
   - Natural language to SQL conversion
   - BigQuery query execution
   - Basic data visualization (charts, tables)
   - Text-based insights and summaries

2. **CLI Interface**
   - Interactive query mode
   - Batch processing mode
   - Configuration management
   - Basic authentication

3. **Token Tracking**
   - Usage monitoring
   - Cost estimation
   - Performance metrics

## Nice-to-Have Features (Post-MVP)
- Advanced access control and user management
- Query caching and optimization
- Advanced visualizations
- Export to multiple formats
- Observability and monitoring
- API endpoints for web interface

## Environment Setup
- Python 3.11+
- Google Cloud SDK for BigQuery access
- Environment variables for API keys
- Virtual environment for dependencies
- Development and production configuration files