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
- **LLM Provider**: Google VertexAI with Google GenAI client (gemini-2.0-flash)
- **Data Source**: Google BigQuery (read-only access)
- **CLI Framework**: Click/Typer
- **Visualization**: Plotly and Matplotlib (both options available, decide later)
- **Containerization**: Docker preferred

### Enhanced AI Agent Components
- **Knowledge Base**: ChromaDB for user_transaction context (local, vector-based, easy setup)
- **Session Management**: SQLite for persistent chat sessions (built-in, reliable, perfect for local storage)
- **Caching**: Redis for processed insights (cache queries >2s execution time)
- **Query Safety**: Date filtering (≤30 days) enforced by AI agents
- **Observability**: JSON logs for agent decision tracking

### ChromaDB Choice Rationale
- **Local deployment**: No external API dependencies 
- **Vector similarity**: Perfect for finding related queries and business context
- **Easy setup**: Pip install, no complex configuration
- **Extensible**: Can easily migrate to Pinecone later if needed
- **Cost-effective**: Free for POC, scales with usage

### Dependencies to Include
- `google-cloud-aiplatform` (VertexAI)
- `google-generativeai` (Google GenAI client)
- `google-cloud-bigquery` (BigQuery access)
- `crewai` (latest version)
- `click`, `typer` (CLI)
- `plotly`, `matplotlib` (visualization options)
- `pydantic`, `loguru`, `rich`, `pandas`, `numpy`
- `chromadb` or `pinecone-client` (knowledge base)
- `redis` (caching)
- `sqlite3` (built-in for sessions)
- `sqlparse` (SQL parsing for date validation)

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
# Format code with ruff
uv run ruff format .

# Lint code with ruff
uv run ruff check .

# Fix auto-fixable issues
uv run ruff check . --fix

# Type checking
uv run mypy src/
```

### Git Workflow
- **Strategy**: Merge (not rebase)
- **Branch naming**: `feature/`, `fix/`, `docs/`
- **Commit format**: Conventional commits (`feat:`, `fix:`, `docs:`, etc.)
- **PRs**: Create draft PRs, reviewer resolves conflicts

## Agent Assignments (MVP-Prioritized)

### Agent 1 (User Interface + Core Safety)
**Branches**: `feature/cli-interface`, `feature/sessions`, `feature/safety`
**MVP Responsibilities**:
- Interactive CLI with slash commands (/sessions, /switch, /new)
- Session management (SQLite) - multiple chat windows
- Date validation and query safety (≤30 days)
- BigQuery client implementation
- Authentication system (Google Cloud)

### Agent 2 (AI Core + Output)
**Branches**: `feature/crew-agents`, `feature/output-system`
**MVP Responsibilities**:
- CrewAI agent configuration
- Query generation agent (NL → SQL with date constraints)
- Data analysis agent
- Basic visualization (Plotly/Matplotlib)
- Response formatting

### Phase 2 Enhancements (Post-MVP)
**Shared responsibilities**:
- Knowledge base implementation (ChromaDB)
- Processed insights caching (Redis)
- Enhanced observability logging
- Advanced safety features

### Reviewer
**Responsibilities**:
- Resolve merge conflicts
- Review draft PRs
- Integration testing
- Code review checklist: tests present, no failing tests

## Architecture Decisions

### Enhanced CrewAI Agent System
1. **Query Agent**: Natural language → SQL conversion with date filtering
2. **Analysis Agent**: Data processing and insights with caching
3. **Visualization Agent**: Charts and summaries
4. **Safety Agent**: Query validation and date range enforcement (≤30 days)

### Enhanced System Flow
```
User Input → Session Manager → Knowledge Base Query → 
CrewAI Agents → Date Validator (≤30 days) → Cache Check → 
BigQuery → Safety Validation → Response + Confidence → 
Session Storage → Observability Log → User
```

### Error Handling & Safety
- **VertexAI failures**: Fail on non-200 responses
- **MAX_TOKEN errors**: Add TODO for handling (don't fail)
- **BigQuery**: Read-only queries, mandatory date filtering
- **Date Range Validation**: Auto-add WHERE clauses, reject queries >30 days
- **Query Safety**: SQL injection prevention, confidence scoring

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

### Phase 1: MVP (Days 1-2)
**Agent 1 Focus:**
- [ ] Interactive CLI with slash commands
- [ ] Session management (SQLite) - multiple chat windows  
- [ ] Date validation and query safety (≤30 days)
- [ ] BigQuery client implementation

**Agent 2 Focus:**
- [ ] CrewAI agent configuration
- [ ] Natural language to SQL conversion (with date constraints)
- [ ] Basic data visualization
- [ ] Response formatting

**Shared:**
- [ ] Token usage tracking
- [ ] Basic error handling

### Phase 2: Enhanced Features (Days 3-4)
- [ ] Knowledge base for user_transaction context (ChromaDB)
- [ ] Processed insights caching (Redis, >2s queries)
- [ ] Enhanced observability logging
- [ ] Confidence scoring
- [ ] Advanced query optimization

### Medium Priority (Days 5+)
- [ ] Enhanced error handling for MAX_TOKEN scenarios
- [ ] Confidence scoring for responses
- [ ] Advanced query optimization suggestions
- [ ] Docker configuration refinement

### Low Priority (Future Enhancements)
- [ ] Integration testing
- [ ] Google authentication with Okta
- [ ] User access control system
- [ ] Advanced visualizations
- [ ] Multi-format export

## Interactive CLI Design

### Slash Commands (Agent 1 Implementation)
```bash
bi-chat  # Start interactive mode

> /help                           # Show all commands
> /sessions                       # List all sessions  
> /new "Sales Q3 Analysis"        # Create new named session
> /switch sales-q3                # Switch to existing session
> /switch                         # List sessions to switch to
> /rename "New Session Name"      # Rename current session
> /delete session-id              # Delete session
> /clear                          # Clear current session history
> /export session.json            # Export session data
> /exit                           # Exit CLI

# Regular queries (no slash prefix)
> show me revenue trends for last week
> what are the top user transactions  
> analyze user behavior patterns
```

### Session Management Flow
1. **Default session**: Auto-created on first use
2. **Named sessions**: User creates with `/new "Analysis Name"`
3. **Session persistence**: All conversations saved to SQLite
4. **Context carryover**: Previous questions inform current responses
5. **Easy switching**: Resume any session anytime

### Date Safety Integration
- Query Agent automatically enforces ≤30 day limit
- Reject queries that would generate >30 day date ranges
- User sees helpful error: "Query would scan too much data. Try: 'last 2 weeks' instead"

## Interface Contracts

### Key Data Models
```python
# Shared interfaces between agents
class QueryResult(BaseModel):
    data: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    execution_time: float
    row_count: int
    date_range: Tuple[datetime, datetime]  # Enforced 30-day limit

class TokenUsage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    cost_estimate: float

class AgentResponse(BaseModel):
    content: str
    visualizations: Optional[List[Dict]]
    token_usage: TokenUsage
    confidence_score: float  # 0.0 - 1.0
    timestamp: datetime
    cached: bool

class UserSession(BaseModel):
    session_id: str
    user_id: str
    title: str
    created_at: datetime
    last_activity: datetime
    conversation_history: List[Dict]

class ObservabilityLog(BaseModel):
    session_id: str
    agent_name: str
    decision_reason: str
    input_query: str
    output_sql: str
    confidence: float
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
2. Format code: `uv run ruff format .`
3. Lint and fix: `uv run ruff check . --fix`
4. Type check: `uv run mypy src/`
5. **Update documentation**: If making technical/architectural changes, update both `CLAUDE.md` and `docs/` files
6. Create draft PR with description

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

## Documentation Maintenance
**CRITICAL**: When making technical/architectural changes, always update:
1. **CLAUDE.md** - This memory file (interface contracts, architecture decisions, workflows)
2. **docs/PROJECT_PLAN.md** - Technical architecture and system design
3. **docs/MULTI_AGENT_WORKFLOW.md** - Agent coordination and responsibilities
4. **docs/CLAUDE_CODE_SETUP.md** - Setup instructions and commands

**Examples of changes requiring doc updates**:
- New dependencies or tech stack changes
- Interface contract modifications (data models, API changes)
- Agent responsibility changes
- New development commands or workflows
- Architecture flow changes
- Safety/security requirement updates
- Environment variable or configuration changes

**Why this matters**: 
- Ensures consistency across multi-agent development
- Prevents context loss between Claude Code sessions
- Maintains accurate project knowledge for new team members
- Keeps setup instructions current and functional