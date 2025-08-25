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
- **Visualization**: Plotly (interactive charts)
- **Session Management**: SQLite for persistent chat sessions
- **Knowledge Base**: ChromaDB for user_transaction context
- **Caching**: Redis for processed insights (>2s queries)
- **Safety**: Date filtering (≤30 days) and query validation
- **Auth**: Service account (/etc/creds/credentials_ai.json)

## Enhanced System Architecture

```
User Input (CLI) → Session Manager (Agent 1) → 
CrewAI Agents (Agent 2) → BigQuery Integration (Agent 2) → 
Data Analysis + Visualization (Agent 2) → 
Response + Confidence → Session Storage (Agent 1) → User
```

### Components:
1. **Interactive CLI** (Agent 1)
   ├── Slash commands (/sessions, /new, /switch)
   ├── Session management (SQLite)
   ├── Date validation and safety
   └── Integration with Agent 2's CrewAI workflow

2. **Enhanced CrewAI Agent System + BigQuery** (Agent 2)
   ├── Query Agent: NL → SQL with date constraints
   ├── Analysis Agent: Data processing with BigQuery integration
   ├── Visualization Agent: Plotly charts & summaries
   └── BigQuery Client: Query execution and data retrieval

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
│   ├── agents/                # Agent 2: CrewAI agents + BigQuery integration
│   │   ├── __init__.py
│   │   ├── crew_setup.py      # CrewAI configuration
│   │   ├── query_agent.py     # NL → SQL with date constraints
│   │   ├── analysis_agent.py  # Data processing & insights
│   │   ├── viz_agent.py       # Visualization generation
│   │   └── tools.py           # BigQuery client + CrewAI tools
│   ├── output/                # Agent 2: Response formatting & visualization
│   │   ├── __init__.py
│   │   ├── formatters.py      # Response formatting
│   │   ├── visualizations.py  # Chart generation (Plotly)
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
│   └── MULTI_AGENT_WORKFLOW.md
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
**Responsibility**: Interactive CLI + Sessions + Safety
**Branches**: 
- `feature/cli-interface`
- `feature/sessions` 
- `feature/safety`

**MVP Tasks (Phase 1)**:
- Interactive CLI with slash commands (/sessions, /new, /switch)
- Session management using SQLite (multiple chat windows)
- Date validation and query safety (≤30 days)
- User authentication and session management
- Integration with Agent 2's CrewAI workflow

**Component Focus**:
- `src/cli/` - Interactive CLI system
- `src/sessions/` - SQLite session management
- `src/safety/` - Date & query validation

### Agent 2 (AI Core + BigQuery + Output System)
**Responsibility**: CrewAI Agents + BigQuery Integration + Visualization + Response Formatting
**Branches**: 
- `feature/crew-agents`
- `feature/output-system`

**MVP Tasks (Phase 1)**:
- CrewAI agent configuration with gemini-2.0-flash
- Query generation agent (NL → SQL with date constraints)
- BigQuery client implementation and query execution
- Data analysis agent with insights generation
- Plotly visualization system
- Response formatting and presentation

**Component Focus**:
- `src/agents/` - CrewAI agent system + BigQuery integration
- `src/output/` - Plotly visualization & formatting

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

---

## Agent 2 - CrewAI Tools Architecture Specification

### **Tool Implementation Location**: `src/agents/tools.py`
### **Total Tools**: 4 CrewAI @tool decorators + 4 utility functions
### **BigQuery Integration**: Agent 2 owns completely

### **Utility Functions (Normal Python functions)**

#### `build_table_name(table_name: str) -> str`
**Purpose**: Constructs full BigQuery table references  
**Example**: `"user_transaction"` → `"data-314708.intermediate_transaction.user_transaction"`  
**Uses**: Environment variables `GOOGLE_CLOUD_PROJECT`, `BIGQUERY_DATASET`

#### `calculate_confidence_score(query_complexity: str, validation_passed: bool, data_quality_score: float) -> float`
**Purpose**: Consistent confidence scoring (0.0-1.0) across all agents

#### `format_error_response(error_type: str, error_message: str, context: dict) -> str`
**Purpose**: Standardized user-friendly error messages with suggestions

#### `validate_date_safety(sql_query: str) -> dict`
**Purpose**: Validates SQL enforces ≤30 day date constraints  
**Returns**: `{"is_safe": bool, "message": str, "suggested_fix": str}`

### **CrewAI Tools (@tool decorators)**

#### 1. `generate_sql_query_tool`
**Agent**: Query Agent  
**Purpose**: Convert natural language to safe BigQuery SQL  
**Input**: `natural_language_query: str, table_name: str`  
**Output**: `str` (enhanced BigQuery SQL with ORDER BY, LIMIT)  
**Features**: 
- Built-in date safety validation (≤30 days)
- Automatic SQL enhancements (ORDER BY, LIMIT)
- BigQuery syntax optimization

#### 2. `execute_bigquery_tool` ⚠️ **AGENT 2 IMPLEMENTS BIGQUERY CLIENT**
**Agent**: Analysis Agent  
**Purpose**: Execute SQL queries against BigQuery using Agent 2's own BigQuery client  
**Input**: `sql_query: str, table_name: str`  
**Output**: `QueryResult` from `src/utils/models.py`  
**Implementation**: **Agent 2 implements BigQuery client directly using `google-cloud-bigquery`**

#### 3. `generate_insights_tool`  
**Agent**: Analysis Agent  
**Purpose**: Comprehensive data analysis and business insights generation  
**Input**: `query_result: QueryResult, original_query: str`  
**Output**: `str` (natural language business insights)  
**Features**:
- Statistical analysis (mean, median, sum, count, std dev)
- Trend detection (patterns, seasonality, anomalies)  
- Business insight generation in natural language

#### 4. `generate_plotly_chart_tool`
**Agent**: Visualization Agent  
**Purpose**: Create appropriate Plotly visualizations  
**Input**: `query_result: QueryResult, original_query: str, title: str`  
**Output**: `dict` (Plotly JSON specification)  
**Features**:
- Automatic chart type recommendation based on data
- Interactive Plotly chart generation
- Optimized for web display

### **Agent 2 BigQuery Integration**

Agent 2 implements BigQuery client directly in `execute_bigquery_tool`:

```python
from google.cloud import bigquery
import os
from datetime import datetime

@tool
def execute_bigquery_tool(sql_query: str, table_name: str) -> QueryResult:
    """Execute BigQuery SQL and return structured result"""
    
    # Initialize BigQuery client
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "data-314708")
    credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    
    client = bigquery.Client(project=project_id)
    
    # Build full table name
    full_table_name = build_table_name(table_name)
    
    # Execute query with error handling
    try:
        start_time = datetime.now()
        query_job = client.query(sql_query)
        results = query_job.result()
        execution_time = (datetime.now() - start_time).total_seconds()
        
        # Convert to QueryResult format
        data = [dict(row) for row in results]
        row_count = len(data)
        
        # Extract date range from data if available
        date_range = extract_date_range(data)
        
        return QueryResult(
            data=data,
            metadata={"job_id": query_job.job_id, "bytes_processed": query_job.total_bytes_processed},
            execution_time=execution_time,
            row_count=row_count,
            date_range=date_range
        )
        
    except Exception as e:
        # Convert BigQuery errors to user-friendly messages
        error_message = format_error_response("BigQuery", str(e), {"query": sql_query})
        raise Exception(error_message)
```

### **Tool Usage Flow**

```python
# Complete Agent 2 workflow (no Agent 1 dependencies):

# 1. Query Agent generates SQL
sql_query = generate_sql_query_tool(
    "show me revenue trends for last week", 
    "user_transaction"
)

# 2. Analysis Agent executes query (Agent 2's BigQuery client)
query_result = execute_bigquery_tool(sql_query, "user_transaction")

# 3. Analysis Agent generates insights
insights = generate_insights_tool(query_result, "revenue trends for last week")

# 4. Visualization Agent creates chart
chart = generate_plotly_chart_tool(
    query_result, 
    "revenue trends for last week",
    "Weekly Revenue Trend Analysis"
)
```