# OpenProject NanoClaw Skill

Centralized multi-project task management for NanoClaw, enabling visibility and coordination across the HP server migration project and concurrent initiatives.

## Overview

This skill integrates OpenProject with NanoClaw, providing:

- **Multi-Project Queries**: View all tasks across projects in a single query
- **Natural Language Interface**: Ask "What am I working on this week?" and get cross-project results
- **Task Management**: Create, update, and link tasks across projects
- **Team Visibility**: See who's working on what across initiatives
- **Date-Based Planning**: Easy weekly/monthly workload views

## Architecture

```
NanoClaw Agent
    ↓
OpenProject Skill (prompt_template.md)
    ↓
openproject_cli.py (HTTP client)
    ↓
OpenProject MCP Server (http://localhost:8085)
    ↓
OpenProject API v3
```

## Prerequisites

1. **OpenProject Instance**: Running instance with API access
2. **OpenProject MCP Server**: Running on port 8085 (default)
3. **Python 3.8+**: For running the CLI wrapper
4. **httpx**: For HTTP client (`pip install httpx`)

## Installation

### Docker Deployment

```bash
docker-compose up -d openproject-mcp
```

### Local Development

```bash
# Install dependencies
pip install -r ../requirements.txt

# Set MCP URL (optional, defaults to http://localhost:8085)
export OPENPROJECT_MCP_URL=http://localhost:8085

# Test the CLI
python openproject_cli.py list_projects
```

## Usage

### Direct CLI

```bash
# List all projects
python openproject_cli.py list_projects

# Get tasks due this week
python openproject_cli.py get_tasks_by_date --date_range "this week"

# Create a task
python openproject_cli.py create_task \
  --project_id 5 \
  --subject "My Task" \
  --due_date "2026-05-22"

# Link tasks
python openproject_cli.py create_dependency \
  --from_task_id 234 \
  --to_task_id 235 \
  --relation_type "follows"
```

### Via NanoClaw

Simply ask natural language questions:

- "What am I working on today?"
- "Show me my workload for this week"
- "Create a task in the HP Server project"
- "Link task 235 to task 234"
- "Who's on the Nutrition Tracker project?"

## Commands

### Project Management

| Command | Purpose |
|---------|---------|
| `list_projects` | Show all accessible projects |
| `create_project` | Create a new project |
| `get_project_summary` | Get project overview (task counts, status) |

### Work Package Management

| Command | Purpose |
|---------|---------|
| `create_task` | Create a work package in a project |
| `get_tasks_by_date` | Query tasks by date range (KILLER FEATURE) |
| `update_task` | Modify task details |

### Dependencies

| Command | Purpose |
|---------|---------|
| `create_dependency` | Link tasks (follows, precedes, blocks, etc.) |

### Team

| Command | Purpose |
|---------|---------|
| `get_project_team` | List project members |

## Date Range Examples

The `get_tasks_by_date` command supports flexible date ranges:

```bash
# Single day
--date_range "today"
--date_range "tomorrow"

# Relative offsets
--date_range "today to +2"      # Today through 2 days ahead
--date_range "today to +7"      # This week

# Named periods
--date_range "this week"        # Mon-Sun of current week
--date_range "next week"        # Mon-Sun of next week
--date_range "this month"       # First to last of current month

# Explicit dates
--date_range "2026-05-21"                              # Single date
--date_range "2026-05-21 to 2026-05-28"               # Date range
```

## Examples

### Daily Standup

```bash
openproject_cli.py get_tasks_by_date --date_range "today" --status open
```

Output:
```json
{
  "success": true,
  "query_date_range": "2026-05-21 to 2026-05-21",
  "work_packages_by_project": [
    {
      "project_id": "5",
      "project_name": "HP Server Build",
      "work_packages": [
        {
          "id": 234,
          "subject": "Pull motherboard from notebook",
          "due_date": "2026-05-21",
          "status": "In Progress",
          "assignee": "George"
        }
      ]
    }
  ]
}
```

### Weekly Planning

```bash
openproject_cli.py get_tasks_by_date --date_range "this week" --status open
```

### Create HP Server Task

```bash
openproject_cli.py create_task \
  --project_id 5 \
  --subject "Pull motherboard from notebook" \
  --description "Carefully disconnect all cables and extract" \
  --due_date "2026-05-22" \
  --estimated_hours 2
```

### Link Tasks

```bash
openproject_cli.py create_dependency \
  --from_task_id 234 \
  --to_task_id 235 \
  --relation_type "follows" \
  --description "Documentation comes after extraction"
```

This creates a Gantt chart dependency in OpenProject showing task 235 depends on task 234.

## Configuration

### Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `OPENPROJECT_MCP_URL` | `http://localhost:8085` | MCP server address |

### Config Files

- `config.yml`: Skill configuration and command definitions
- `manifest.json`: Full skill metadata and deployment config
- `prompt_template.md`: NanoClaw prompt routing and examples

## Architecture Decisions

### Why This Design?

1. **Thin CLI Wrapper**: Keeps OpenProject MCP as source of truth
2. **No Database Duplication**: All data stays in OpenProject
3. **Stateless**: CLI is stateless HTTP client
4. **Scalable**: Works with N projects automatically
5. **Transparent**: All data visible via OpenProject UI and API

### Key Feature: `get_work_packages_by_date_range`

This is the centerpiece that enables multi-project querying. It:
- Queries OpenProject API v3 with date filters
- Returns results grouped by project
- Works across all projects user can access
- Supports status filtering (open/closed/all)
- Sorts by due date automatically

This is what makes "What am I working on this week?" queries possible across projects.

## Testing

### Unit Tests

```bash
cd ..
pytest tests/test_nanoclaw_integration.py -v
```

### Integration Tests

```bash
# Start MCP server
python src/mcp_server.py &

# Test CLI
python nanoclaw_skill/openproject_cli.py list_projects
python nanoclaw_skill/openproject_cli.py get_tasks_by_date --date_range "today"
```

### Manual Testing

```bash
# Create test project
python openproject_cli.py create_project --name "Test Project"

# Create test task
python openproject_cli.py create_task \
  --project_id 999 \
  --subject "Test Task" \
  --due_date "2026-05-22"

# Query it
python openproject_cli.py get_tasks_by_date --date_range "2026-05-22"
```

## Troubleshooting

### "Connection refused" errors

Check MCP server is running:
```bash
curl http://localhost:8085/tools
```

### "Project ID must be positive integer"

Verify project ID is correct:
```bash
python openproject_cli.py list_projects
```

### Date range not recognized

Check format against examples above. Date ranges are case-insensitive:
```bash
# These all work:
--date_range "today"
--date_range "Today"
--date_range "THIS WEEK"
```

## Future Enhancements

Post-MVP features (see manifest.json for details):

- Custom filters by assignee, status, priority
- Gantt chart visualization export
- Time tracking integration
- Automated task templates
- Budget/resource allocation
- Custom field support
- Slack/Teams notifications

## Development

### File Structure

```
nanoclaw_skill/
├── openproject_cli.py       # Main CLI implementation
├── prompt_template.md       # NanoClaw prompt routing
├── manifest.json            # Skill metadata
├── config.yml               # Configuration
├── __init__.py              # Package init
└── README.md                # This file
```

### Adding New Commands

1. Add method to `OpenProjectCLI` class in `openproject_cli.py`
2. Add CLI argument parser in `main()`
3. Route to command in command handler
4. Add to `manifest.json` capabilities
5. Update prompt_template.md with examples

Example:
```python
def new_command(self, arg1: str) -> Dict[str, Any]:
    """Description of command."""
    return self._call_tool_sync("mcp_tool_name", arg1=arg1)
```

## Support

For issues or questions:
1. Check prompt_template.md for command examples
2. Review manifest.json for command definitions
3. Check MCP server logs for API errors
4. Verify OpenProject instance is accessible

## License

Part of the OpenProject MCP Server integration.
