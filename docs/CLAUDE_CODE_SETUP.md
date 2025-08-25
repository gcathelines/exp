# Claude Code Multi-Session Setup Guide

## Quick Start for Multiple Claude Code Sessions

### Step 1: Initialize Project (Do Once)
On your main device, run these commands:

```bash
# Create project directory and initialize git
mkdir bi-chat-cli
cd bi-chat-cli
git init
git branch -M main

# Create initial project structure
mkdir -p src/{cli,agents,data,output,utils}
mkdir -p tests/{unit,integration,fixtures}
mkdir -p config docs

# Initialize uv project
uv init --python 3.11
uv add click typer crewai google-cloud-bigquery pydantic plotly matplotlib loguru python-dotenv rich httpx pandas numpy
uv add --dev pytest pytest-cov pytest-asyncio black ruff mypy pre-commit

# Add documentation files to docs folder
# (docs/PROJECT_PLAN.md and docs/MULTI_AGENT_WORKFLOW.md should already be created)

# Create and push to remote repository
git remote add origin <your-repository-url>
git add .
git commit -m "initial: project setup with uv and documentation"
git push -u origin main
```

### Step 2: Device 1 - Agent 1 Setup (CLI + Data Layer)

```bash
# Navigate to project (if not already there)
cd bi-chat-cli

# Start a new Claude Code session and say:
"I'm Agent 1 for the BI Chat CLI project. Please read docs/PROJECT_PLAN.md to understand my role. I'm responsible for CLI interface and data layer. Start by creating the branch feature/cli-interface and begin implementing the CLI structure according to the project plan."
```

### Step 3: Device 2 - Agent 2 Setup (CrewAI + Output)

```bash
# Clone the repository
git clone <your-repository-url>
cd bi-chat-cli

# Start a new Claude Code session and say:
"I'm Agent 2 for the BI Chat CLI project. Please read docs/PROJECT_PLAN.md to understand my role. I'm responsible for CrewAI agents and output system. Start by creating the branch feature/crew-agents and begin implementing the agent system according to the project plan."
```

## Detailed Instructions for Each Agent

### Agent 1 Commands (CLI + Data Layer)

**Initial Setup:**
```
Read docs/PROJECT_PLAN.md and docs/MULTI_AGENT_WORKFLOW.md. I'm Agent 1 responsible for:
1. CLI interface implementation using Click/Typer
2. BigQuery data layer and connections
3. Authentication system

Create branch feature/cli-interface and start with the CLI structure. Follow the interface contracts defined in docs/PROJECT_PLAN.md.
```

**Task Switching:**
```
I've completed the CLI interface work. Please commit the changes, push to feature/cli-interface, and switch to feature/data-layer branch. Start implementing the BigQuery client according to docs/PROJECT_PLAN.md.
```

**Status Updates:**
```
Provide a status update on Agent 1 progress. List completed tasks, current work, and any blockers. Push all changes to the appropriate branches.
```

### Agent 2 Commands (CrewAI + Output)

**Initial Setup:**
```
Read docs/PROJECT_PLAN.md and docs/MULTI_AGENT_WORKFLOW.md. I'm Agent 2 responsible for:
1. CrewAI agent system implementation
2. Output formatting and visualization
3. Response generation

Create branch feature/crew-agents and start with the CrewAI configuration. Follow the interface contracts defined in docs/PROJECT_PLAN.md.
```

**Task Switching:**
```
I've completed the CrewAI agents work. Please commit the changes, push to feature/crew-agents, and switch to feature/output-system branch. Start implementing the visualization and output formatting according to docs/PROJECT_PLAN.md.
```

**Status Updates:**
```
Provide a status update on Agent 2 progress. List completed tasks, current work, and any blockers. Push all changes to the appropriate branches.
```

## Coordination Commands

### For Both Agents - Sync Check:
```
Pull the latest changes from all branches and check if there are any interface changes from the other agent that affect my work. Review any PRs or commits from the other agent.
```

### For Both Agents - Integration Preparation:
```
My module is complete. Please:
1. Run all tests and ensure they pass
2. Create a comprehensive PR with proper description
3. Document any interface changes in docs/PROJECT_PLAN.md
4. Prepare for integration with the other agent's work
```

## Repository Structure Commands

### Creating Initial Project Structure:
```bash
# This should be done once by the first agent or manually
mkdir -p src/{cli,agents,data,output,utils}
mkdir -p tests/{unit,integration,fixtures}
mkdir -p config docs

# Initialize with uv
uv init --python 3.11
uv add click typer crewai google-cloud-bigquery pydantic plotly matplotlib loguru python-dotenv rich httpx pandas numpy
uv add --dev pytest pytest-cov pytest-asyncio black ruff mypy pre-commit

# Create empty __init__.py files
touch src/__init__.py
touch src/cli/__init__.py
touch src/agents/__init__.py
touch src/data/__init__.py
touch src/output/__init__.py
touch src/utils/__init__.py

# pyproject.toml is automatically created by uv
```

## Troubleshooting

### Common Issues:

1. **"Project not found"**
   ```
   Read docs/PROJECT_PLAN.md and docs/MULTI_AGENT_WORKFLOW.md files to understand the project context.
   ```

2. **"Branch conflicts"**
   ```
   Pull the latest changes from main branch and rebase your feature branch. Resolve any conflicts according to the interface contracts in docs/PROJECT_PLAN.md.
   ```

3. **"Missing dependencies"**
   ```
   Check if the other agent has implemented the required interfaces. If not, create mock implementations based on the contracts in docs/PROJECT_PLAN.md.
   ```

4. **"Integration issues"**
   ```
   Review the interface contracts in docs/PROJECT_PLAN.md and ensure both agents are following the same data models and function signatures.
   ```

## Success Verification

After setup, each agent should be able to:
- [ ] Read and understand docs/PROJECT_PLAN.md
- [ ] Create their assigned feature branches
- [ ] Start implementing their modules independently
- [ ] Follow the defined interface contracts
- [ ] Commit and push changes regularly
- [ ] Coordinate through git branches and PRs

## Next Steps After Setup

1. Agent 1: Implement CLI interface and BigQuery connection
2. Agent 2: Implement CrewAI agents and output system
3. Regular sync every 4-6 hours
4. Integration testing by reviewer
5. Final testing and deployment preparation