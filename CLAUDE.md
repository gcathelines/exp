# BI Chat CLI - Claude Code Memory

## Project Overview
**Purpose**: Business Intelligence Chat CLI enabling non-technical users to analyze BigQuery data using natural language queries through CrewAI agents.

**Timeline**: 2 days development with 2 Claude Code agents + 1 reviewer

**Target Users**: Internal developers (primary), business analysts (future)

## Key Technologies & Decisions

### Core Stack
- **Language**: Python 3.11+
- **Package Manager**: `uv` (ALWAYS use uv, never pip)
- **Agent Framework**: CrewAI (pin to latest version)
- **LLM Provider**: Google VertexAI with Google GenAI client
- **Data Source**: Google BigQuery (read-only access)
- **CLI Framework**: Click/Typer
- **Visualization**: Plotly and Matplotlib (both options available, decide later)
- **Containerization**: Docker preferred

### Dependencies to Include
- `google-cloud-aiplatform` (VertexAI)
- `google-generativeai` (Google GenAI client)
- `google-cloud-bigquery` (BigQuery access)
- `crewai` (latest version)
- `click`, `typer` (CLI)
- `plotly`, `matplotlib` (visualization options)
- `pydantic`, `loguru`, `rich`, `pandas`, `numpy`

## Development Commands

### Package Management
```bash
# Install dependencies
uv sync

# Add new dependency
uv add package-name

# Add dev dependency  
uv add --dev package-name

# Run commands
uv run command
```

### Testing
```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src

# Run specific test type
uv run pytest tests/unit/
uv run pytest tests/integration/  # lowest priority
```

### Code Quality
```bash
# Format code
uv run black .

# Lint code
uv run ruff check .

# Type checking
uv run mypy src/
```

### Git Workflow
- **Strategy**: Merge (not rebase)
- **Branch naming**: `feature/`, `fix/`, `docs/`
- **Commit format**: Conventional commits (`feat:`, `fix:`, `docs:`, etc.)
- **PRs**: Create draft PRs, reviewer resolves conflicts

## Agent Assignments

### Agent 1 (CLI + Data Layer)
**Branches**: `feature/cli-interface`, `feature/data-layer`
**Responsibilities**:
- CLI commands using Click/Typer
- BigQuery client implementation
- Authentication system (Google Cloud)
- Schema discovery service
- Query execution engine

### Agent 2 (CrewAI + Output)
**Branches**: `feature/crew-agents`, `feature/output-system`
**Responsibilities**:
- CrewAI agent configuration
- Query generation agent (NL → SQL)
- Data analysis agent
- Visualization agent (Plotly/Matplotlib)
- Response formatting

### Reviewer
**Responsibilities**:
- Resolve merge conflicts
- Review draft PRs
- Integration testing
- Code review checklist: tests present, no failing tests

## Architecture Decisions

### CrewAI Agent System
1. **Query Agent**: Natural language → SQL conversion
2. **Analysis Agent**: Data processing and insights
3. **Visualization Agent**: Charts and summaries

### Error Handling
- **VertexAI failures**: Fail on non-200 responses
- **MAX_TOKEN errors**: Add TODO for handling (don't fail)
- **BigQuery**: Read-only queries, validate before execution

### Testing Strategy
- **Unit tests**: Mock BigQuery/VertexAI with realistic data/responses
- **Integration tests**: Nice to have, lowest priority
- **Coverage**: Target >90% but not enforced
- **Mocking**: Use realistic responses close to actual API responses

## Project Structure
```
bi-chat-cli/
├── src/
│   ├── cli/           # CLI interface (Agent 1)
│   ├── agents/        # CrewAI agents (Agent 2)
│   ├── data/          # BigQuery layer (Agent 1)
│   ├── output/        # Visualization (Agent 2)
│   └── utils/         # Shared utilities
├── tests/             # Test suite
├── docs/              # Documentation
└── config/            # Configuration
```

## TODOs and Future Enhancements

### High Priority (MVP)
- [ ] Natural language to SQL conversion
- [ ] BigQuery query execution
- [ ] Basic data visualization
- [ ] CLI interface with interactive mode
- [ ] Token usage tracking

### Medium Priority
- [ ] Explore BigQuery schema: `data-314708.intermediate_transaction.user_transaction`
- [ ] Docker configuration
- [ ] Query caching
- [ ] Enhanced error handling for MAX_TOKEN scenarios

### Low Priority (Nice to Have)
- [ ] Integration testing
- [ ] Comprehensive logging system
- [ ] Google authentication with Okta
- [ ] User access control system
- [ ] Advanced visualizations
- [ ] Multi-format export

## Interface Contracts

### Key Data Models
```python
# Shared interfaces between agents
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
```

## Configuration
- **Environment**: Use `.env` files
- **Google Cloud**: Service account authentication at `/etc/creds/credentials_ai.json`
- **VertexAI**: Project `ai-engineering-210825`, region `us-central1`
- **BigQuery**: Project `data-314708`, dataset `intermediate_transaction`, table `user_transaction` (read-only)

## Common Workflows

### Starting Work
1. Read this file and `docs/PROJECT_PLAN.md`
2. Check current branch and pull latest
3. Create/switch to appropriate feature branch
4. Install dependencies: `uv sync`

### Before Committing
1. Run tests: `uv run pytest`
2. Format code: `uv run black .`
3. Lint: `uv run ruff check .`
4. Create draft PR with description

### Integration Points
- Sync every 4-6 hours between agents
- Use interface contracts for compatibility
- Reviewer handles final integration

## Development Environment
- **Preferred**: Docker containers
- **Python Version**: 3.11+ (specified in `.python-version`)
- **IDE**: Any (VSCode configurations welcome)
- **Cloud**: Google Cloud Platform

## Notes
- Always use `uv` for package management
- BigQuery queries are read-only for security
- VertexAI is the primary LLM provider
- Docker is preferred for deployment
- Focus on MVP features first, nice-to-have items are low priority