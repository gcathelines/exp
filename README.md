# BI Chat CLI

A Business Intelligence Chat CLI that enables non-technical users to analyze BigQuery data using natural language queries through CrewAI agents.

## Quick Start

### Prerequisites
- Python 3.11+
- [uv](https://docs.astral.sh/uv/) package manager
- Google Cloud account with BigQuery access

### Installation
```bash
# Clone the repository
git clone <repository-url>
cd bi-chat-cli

# Install dependencies with uv
uv sync

# Activate the virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### Usage
```bash
# Basic query
bi-chat "Show me sales data for the last quarter"

# Interactive mode
bi-chat --interactive

# Help
bi-chat --help
```

## Project Structure
```
bi-chat-cli/
├── src/
│   ├── cli/           # CLI interface and commands
│   ├── agents/        # CrewAI agent implementations
│   ├── data/          # BigQuery data layer
│   ├── output/        # Response formatting and visualization
│   └── utils/         # Utilities and configuration
├── tests/             # Test suite
├── docs/              # Project documentation
└── config/            # Configuration files
```

## Documentation

- [Project Plan](docs/PROJECT_PLAN.md) - Complete technical specification
- [Multi-Agent Workflow](docs/MULTI_AGENT_WORKFLOW.md) - Development coordination guide
- [Setup Guide](docs/CLAUDE_CODE_SETUP.md) - Multi-session development setup

## Development

### Setup Development Environment
```bash
# Install development dependencies
uv sync --dev

# Install pre-commit hooks
pre-commit install

# Run tests
uv run pytest

# Format code
uv run black .
uv run ruff check .

# Type checking
uv run mypy src/
```

### Multi-Agent Development
This project is designed for parallel development by multiple Claude Code agents. See [Multi-Agent Workflow](docs/MULTI_AGENT_WORKFLOW.md) for coordination details.

## Features

### Current (MVP)
- Natural language to SQL conversion
- BigQuery query execution
- Basic data visualization
- CLI interface with interactive mode
- Token usage tracking

### Planned
- Advanced access control
- Query caching and optimization
- Enhanced visualizations
- Multi-format export
- Web interface

## Architecture

The system uses CrewAI to orchestrate three specialized agents:
1. **Query Agent**: Converts natural language to SQL
2. **Analysis Agent**: Processes data and generates insights
3. **Visualization Agent**: Creates charts and summaries

## Configuration

Create a `.env` file with your configuration:
```bash
GOOGLE_CLOUD_PROJECT=your-project-id
BIGQUERY_DATASET=your-dataset
ANTHROPIC_API_KEY=your-api-key
LOG_LEVEL=INFO
```

## Contributing

1. Read the [Project Plan](docs/PROJECT_PLAN.md) for technical details
2. Follow the [Multi-Agent Workflow](docs/MULTI_AGENT_WORKFLOW.md) for coordination
3. Ensure all tests pass and code is formatted
4. Create descriptive pull requests

## License

MIT License - see LICENSE file for details.