# Multi-Agent Development Workflow Guide

## Overview
This guide explains how to coordinate 2 Claude Code agents working on the BI Chat CLI project simultaneously from different devices/sessions.

## Pre-Setup Requirements

### Git Repository Setup
1. Initialize the repository on the main device:
   ```bash
   git init bi-chat-cli
   cd bi-chat-cli
   git branch -M main
   ```

2. Create remote repository (GitHub/GitLab) and push:
   ```bash
   git remote add origin <repository-url>
   git push -u origin main
   ```

## Agent Session Setup

### Device 1 - Agent 1 (User Interface + Core Safety)
**Location**: Current device
**Branches**: `feature/cli-interface`, `feature/sessions`, `feature/safety`

#### Setup Steps:
1. Clone/navigate to project directory
2. Create and switch to feature branch:
   ```bash
   git checkout -b feature/cli-interface
   ```
3. Tell Claude Code Agent 1:
   ```
   I'm Agent 1 working on the BI Chat CLI project. Please read CLAUDE.md and docs/PROJECT_PLAN.md 
   to understand your role. You're responsible for:
   - Interactive CLI with slash commands (/sessions, /new, /switch)
   - Session management using SQLite (multiple chat windows)
   - Date validation and query safety (≤30 days)
   - BigQuery client implementation
   - Service account authentication
   
   Start implementing the interactive CLI system on branch feature/cli-interface.
   Focus on MVP Phase 1 features first.
   ```

### Device 2 - Agent 2 (AI Core + Output System)
**Location**: Different device/session
**Branches**: `feature/crew-agents`, `feature/output-system`

#### Setup Steps:
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd bi-chat-cli
   ```
2. Create and switch to feature branch:
   ```bash
   git checkout -b feature/crew-agents
   ```
3. Tell Claude Code Agent 2:
   ```
   I'm Agent 2 working on the BI Chat CLI project. Please read CLAUDE.md and docs/PROJECT_PLAN.md 
   to understand your role. You're responsible for:
   - CrewAI agent configuration with gemini-2.0-flash
   - Query generation agent (NL → SQL with date constraints)
   - Data analysis agent with basic insights
   - Visualization system (Plotly/Matplotlib)
   - Response formatting and presentation
   
   Start implementing the CrewAI agent system on branch feature/crew-agents.
   Focus on MVP Phase 1 features first.
   ```

## Coordination Protocol

### Daily Sync Points
**Time**: Every 4-6 hours or after major milestones
**Process**:
1. Both agents push current work to their branches
2. Review each other's progress via GitHub/GitLab
3. Communicate any interface changes needed
4. Update shared interface contracts if needed

### Branch Management
```
main
├── feature/cli-interface      # Agent 1 primary
├── feature/data-layer         # Agent 1 secondary
├── feature/crew-agents        # Agent 2 primary
├── feature/output-system      # Agent 2 secondary
└── integration/staging        # Reviewer for testing
```

### Communication Commands for Agents

#### When Starting Work:
```
Pull latest changes and start working on [feature-name]. 
Check PROJECT_PLAN.md for interface contracts and ensure compatibility 
with other agent's work.
```

#### When Completing a Module:
```
I've completed [module-name]. Please:
1. Run tests to ensure everything works
2. Push changes to branch [branch-name]
3. Create PR with description of changes
4. Update PROJECT_PLAN.md if interfaces changed
```

#### When Switching Tasks:
```
Switching from [current-task] to [new-task]. 
Please commit current progress and switch to branch [new-branch-name].
```

## Conflict Resolution

### Interface Changes
If an agent needs to modify shared interfaces:
1. Document the change in PROJECT_PLAN.md
2. Create a comment in the relevant PR
3. Coordinate with the other agent before merging

### Dependency Issues
If Agent 2 needs Agent 1's work:
1. Create mock/stub implementations
2. Use the interface contracts from PROJECT_PLAN.md
3. Implement integration tests for later validation

### Merge Conflicts
1. Always pull latest main before creating PRs
2. Use rebase workflow to maintain clean history
3. Reviewer handles final integration conflicts

## Testing Strategy

### Individual Agent Testing
Each agent should:
- Write unit tests for their modules
- Use mocks for dependencies not yet implemented
- Test against interface contracts

### Integration Testing
Reviewer coordinates:
- Integration testing between modules
- End-to-end testing of complete workflows
- Performance and token usage validation

## Example Commands for Each Session

### For Agent 1 Session:
```bash
# Initial setup
git checkout -b feature/cli-interface
pip install -r requirements.txt

# During development
git add .
git commit -m "feat: implement CLI command structure"
git push origin feature/cli-interface

# Switching tasks
git checkout -b feature/data-layer
```

### For Agent 2 Session:
```bash
# Initial setup
git clone <repo-url>
cd bi-chat-cli
git checkout -b feature/crew-agents
pip install -r requirements.txt

# During development
git add .
git commit -m "feat: implement CrewAI agent configuration"
git push origin feature/crew-agents

# Switching tasks
git checkout -b feature/output-system
```

## Status Reporting
Each agent should provide status updates in this format:

```
## Agent [1/2] Status Report - [Date/Time]

### Completed:
- [Task 1]
- [Task 2]

### In Progress:
- [Current task]

### Next:
- [Planned next task]

### Blockers:
- [Any dependencies or issues]

### Interface Changes:
- [Any modifications to shared contracts]
```

## Emergency Coordination
If agents need immediate coordination:
1. Create an issue in the GitHub repository
2. Use descriptive titles: `[URGENT] Interface change needed for [module]`
3. Tag with appropriate labels: `coordination`, `interface`, `blocker`

## Success Criteria
- Both agents can work independently 80% of the time
- Clean integration with minimal conflicts
- All interface contracts respected
- MVP completed within 2-day timeline
- Code quality standards maintained across all modules