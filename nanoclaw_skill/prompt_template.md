# OpenProject NanoClaw Skill Prompt Template

You have access to the OpenProject skill for centralized project management across multiple concurrent initiatives.

## Available Commands

Use the following commands based on user intent:

### Project Management

**List all projects:**
```
openproject_cli.py list_projects
```

**Create a new project:**
```
openproject_cli.py create_project --name "{project_name}" --description "{description}"
```

**Get project overview:**
```
openproject_cli.py get_project_summary --project_id {project_id}
```

### Work Package Management (Tasks)

**Create a task:**
```
openproject_cli.py create_task \
  --project_id {project_id} \
  --subject "{task_title}" \
  --description "{description}" \
  --due_date "{YYYY-MM-DD}" \
  --assignee_email "{email@example.com}" \
  --estimated_hours {hours}
```

**Get tasks by date (THE KILLER FEATURE):**
```
openproject_cli.py get_tasks_by_date \
  --date_range "{date_range}" \
  --projects {project_scope} \
  --status {status}
```

Date range formats:
- `"today"` → Today only
- `"tomorrow"` → Tomorrow only
- `"today to +N"` → Today through N days ahead (e.g., "today to +2")
- `"this week"` → Monday through Sunday of current week
- `"next week"` → Monday through Sunday of next week
- `"this month"` → First to last day of current month
- `"next month"` → First to last day of next month
- `"YYYY-MM-DD"` → Specific date (e.g., "2026-05-21")
- `"YYYY-MM-DD to YYYY-MM-DD"` → Date range (e.g., "2026-05-21 to 2026-05-28")

Project scope:
- `"all"` → All projects user can access
- `"1,2,3"` → Specific project IDs (comma-separated)

Status:
- `"open"` → Open/in-progress tasks (default)
- `"closed"` → Completed tasks
- `"all"` → All statuses

**Update a task:**
```
openproject_cli.py update_task \
  --task_id {work_package_id} \
  --subject "{new_title}" \
  --status "{new_status}" \
  --due_date "{YYYY-MM-DD}" \
  --assignee_email "{email@example.com}"
```

### Task Dependencies

**Link tasks together:**
```
openproject_cli.py create_dependency \
  --from_task_id {source_task_id} \
  --to_task_id {target_task_id} \
  --relation_type "follows" \
  --description "{why they are linked}"
```

Relation types:
- `"follows"` → Target task depends on source task (source must finish first)
- `"precedes"` → Source task comes before target task
- `"blocks"` → Source task blocks target task
- `"relates"` → General relationship

### Team Management

**List project team:**
```
openproject_cli.py get_project_team --project_id {project_id}
```

## Examples

### Daily Agenda
User: "What am I working on today?"
```
openproject_cli.py get_tasks_by_date --date_range "today" --status open
```

### Weekly Outlook
User: "Show me my workload for this week"
```
openproject_cli.py get_tasks_by_date --date_range "this week" --status open
```

### Task Planning
User: "Create a task in the HP Server project to pull the motherboard, due tomorrow"
```
openproject_cli.py create_task \
  --project_id 5 \
  --subject "Pull motherboard from notebook" \
  --due_date "2026-05-22" \
  --description "Carefully disconnect all cables and extract motherboard"
```

### Task Dependencies
User: "The documentation task depends on pulling the motherboard first"
```
openproject_cli.py create_dependency \
  --from_task_id 234 \
  --to_task_id 235 \
  --relation_type "follows" \
  --description "Cannot document until motherboard is extracted"
```

### Multi-Project View
User: "Show me all tasks due next week across the HP Server and Nutrition projects"
```
openproject_cli.py get_tasks_by_date \
  --date_range "next week" \
  --projects "5,2" \
  --status open
```

### Status Update
User: "I finished the motherboard extraction task"
```
openproject_cli.py update_task \
  --task_id 234 \
  --status "Closed"
```

### Project Overview
User: "What's the status of the HP Server Build project?"
```
openproject_cli.py get_project_summary --project_id 5
```

## Command Routing Rules

Route user intent to commands as follows:

1. **Daily/Weekly/Date-Based Queries**
   - "What am I working on..." → `get_tasks_by_date`
   - "Show me tasks due..." → `get_tasks_by_date`
   - "What's my workload..." → `get_tasks_by_date`
   - "List tasks between..." → `get_tasks_by_date`

2. **Task Creation**
   - "Create a task..." → `create_task`
   - "Add a new task..." → `create_task`
   - "I need to track..." → `create_task`

3. **Task Updates**
   - "I finished..." / "I completed..." → `update_task --status Closed`
   - "I'm working on..." → `update_task --status "In Progress"`
   - "Change the due date..." → `update_task --due_date`
   - "Assign this to..." → `update_task --assignee_email`

4. **Task Dependencies**
   - "...depends on..." / "...followed by..." → `create_dependency`
   - "Link task X to task Y" → `create_dependency`
   - "Task X blocks task Y" → `create_dependency --relation_type blocks`

5. **Project Management**
   - "Show me all projects" / "List projects" → `list_projects`
   - "Create a new project" → `create_project`
   - "What's the status of project X?" → `get_project_summary`

6. **Team Queries**
   - "Who's on the X project?" / "Show team members" → `get_project_team`

## Multi-Project Querying

The `get_tasks_by_date` command is the centerpiece for NanoClaw integration. It enables:
- Single-query view across all projects
- Filtering by date range
- Status-based filtering
- Project-specific filtering

Example workflow:
```
User: "What's my full workload this week?"
↓
Your response: Let me check all your tasks across projects for this week...
↓
openproject_cli.py get_tasks_by_date --date_range "this week" --status open
↓
Returned tasks grouped by project
↓
"You have 12 tasks this week:
 - HP Server Build: 3 tasks (motherboard extraction, documentation, testing)
 - Nutrition Tracker: 2 tasks (OCR integration, data cleanup)
 - Other projects: 7 tasks"
```

## Output Format

All commands return JSON. Format the response for the user:
- For queries: Present grouped by project, sorted by due date
- For creates/updates: Confirm the action with relevant details
- For errors: Explain what went wrong in plain language

## Error Handling

If a command fails:
1. Check the error message
2. Explain it to the user in plain language
3. Suggest the correct format or action

Common errors:
- "Project ID must be a positive integer" → User provided invalid project ID
- "Start date must be in YYYY-MM-DD format" → Invalid date format
- "Invalid date range" → Date range string not recognized

## Configuration

Environment variables:
- `OPENPROJECT_MCP_URL`: URL of the MCP server (default: http://localhost:8085)

Example in shell:
```bash
export OPENPROJECT_MCP_URL=http://openproject-mcp:8085
openproject_cli.py list_projects
```

## Key Features Enabled by This Integration

✅ **Multi-Project Visibility**: See all work across initiatives in one view
✅ **Natural Language Queries**: Ask "What's due next week?" and get cross-project results
✅ **Date-Based Planning**: Easy weekly/monthly outlooks
✅ **Task Dependencies**: Link tasks to show critical paths
✅ **Team Transparency**: View who's working on what
✅ **Centralized Updates**: Update task status and dates across projects
✅ **Project Summaries**: Quick overview of project health

## Future Enhancements

These can be added as MCP tools expand:
- Custom filters by assignee, priority, status
- Gantt chart export
- Time tracking integration
- Automated task templates
- Budget tracking
- Slack/Teams notifications
