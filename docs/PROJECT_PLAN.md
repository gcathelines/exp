# BI Chat CLI - Project Documentation

## Project Overview
**Purpose**: Business Intelligence Chat CLI for internal developers and business analysts
**Goal**: Enable non-technical users to gather insights from BigQuery data without SQL knowledge
**Timeline**: 2 days
**Team**: 2 Claude Code agents + 1 reviewer developer

## Technical Stack
- **Language**: Python 3.11+
- **Agent Framework**: CrewAI
- **Data Source**: Google BigQuery
- **CLI Framework**: Click/Typer
- **LLM Provider**: Anthropic Claude/OpenAI GPT
- **Query Generation**: LangChain SQL Agent
- **Visualization**: Plotly/Matplotlib
- **Token Tracking**: Custom middleware + LangSmith/Weights & Biases
- **Auth**: JWT/API key system
- **Logging**: Structured logging with loguru

## System Architecture

```
User Input → CLI Interface → CrewAI Agents → BigQuery → Response Generation → CLI Output

1. CLI Entry Point
   ├── Authentication/Authorization
   ├── Input Parsing & Validation
   └── Agent Orchestration

2. CrewAI Agent System
   ├── Query Agent: Natural language → SQL
   ├── Analysis Agent: Data processing & insights
   └── Visualization Agent: Charts & summaries

3. Data Layer
   ├── BigQuery Connection Manager
   ├── Schema Discovery Service
   └── Query Execution Engine

4. Output Layer
   ├── Text Summaries
   ├── Chart Generation
   └── Token Usage Reports
```

## Project Structure

```
bi-chat-cli/
├── src/
│   ├── cli/                    # Branch: feature/cli-interface
│   │   ├── __init__.py
│   │   ├── main.py            # CLI entry point
│   │   ├── commands.py        # CLI command definitions
│   │   └── auth.py            # Authentication middleware
│   ├── agents/                # Branch: feature/crew-agents
│   │   ├── __init__.py
│   │   ├── crew_setup.py      # CrewAI configuration
│   │   ├── query_agent.py     # SQL generation agent
│   │   ├── analysis_agent.py  # Data analysis agent
│   │   └── viz_agent.py       # Visualization agent
│   ├── data/                  # Branch: feature/data-layer
│   │   ├── __init__.py
│   │   ├── bigquery_client.py # BigQuery connection
│   │   ├── schema_discovery.py # Table/schema introspection
│   │   └── query_executor.py  # Query execution & caching
│   ├── output/                # Branch: feature/output-system
│   │   ├── __init__.py
│   │   ├── formatters.py      # Response formatting
│   │   ├── visualizations.py  # Chart generation
│   │   └── exporters.py       # Export utilities
│   └── utils/                 # Branch: feature/utilities
│       ├── __init__.py
│       ├── config.py          # Configuration management
│       ├── logging.py         # Structured logging
│       ├── token_tracker.py   # Token usage tracking
│       └── security.py        # Access control
├── tests/
│   ├── unit/
│   ├── integration/
│   └── fixtures/
├── config/
│   ├── development.yaml
│   └── production.yaml
├── requirements.txt
├── pyproject.toml
├── README.md
└── .env.example
```

## Agent Assignments

### Agent 1 (Claude Code Session #1)
**Responsibility**: CLI Interface + Data Layer
**Branches**: 
- `feature/cli-interface`
- `feature/data-layer`

**Tasks**:
- CLI command structure using Click/Typer
- Authentication and authorization system
- BigQuery client implementation
- Schema discovery service
- Query execution engine
- Error handling and validation

### Agent 2 (Claude Code Session #2)
**Responsibility**: CrewAI Agents + Output System
**Branches**: 
- `feature/crew-agents`
- `feature/output-system`

**Tasks**:
- CrewAI agent configuration
- Query generation agent (NL → SQL)
- Data analysis agent
- Visualization agent
- Response formatting
- Chart generation with Plotly
- Export utilities

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