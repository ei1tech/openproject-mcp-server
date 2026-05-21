# NanoClaw OpenProject Integration Testing Plan

Complete end-to-end testing guide for the OpenProject MCP Server and NanoClaw skill integration.

**Test Date**: 2026-05-21
**Version**: 1.0.0

## Pre-Test Setup

### 1. Environment Verification

Before running tests, verify:

```bash
# Check Python version
python --version  # Should be 3.8+

# Check dependencies
pip list | grep httpx  # Should be installed

# Check OpenProject instance
curl http://localhost:3000  # Should respond with OpenProject

# Check MCP server is running
curl http://localhost:8085/tools  # Should return available tools
```

### 2. Test Data Setup

Create these test projects in OpenProject (or use existing ones):

```
Test Project 1: HP Server Build (ID: 5)
Test Project 2: Nutrition Tracker (ID: 2)
Test Project 3: Other Concurrent Project (ID: 999)
```

Create sample users:
- george@example.com (already exists)
- test-user@example.com (create if needed)

---

## Test Cases

### Test Suite 1: MCP Server Health & Connectivity

#### TC1.1: Health Check Tool
```
Command: curl -X POST http://localhost:8085/tools/health_check
Expected: 200 OK, JSON with status="healthy"
Verify: 
  - openproject_connection: connected
  - openproject_version: present
  - openproject_url: correct
```

#### TC1.2: Test Connection to OpenProject
```
Expected: MCP server successfully connects to OpenProject API
Verify: Credentials are correct, API is accessible
```

### Test Suite 2: Date Range Query Tool

#### TC2.1: Query Today's Tasks
```
Endpoint: /tools/get_work_packages_by_date_range
Payload: {
  "start_date": "2026-05-21",
  "end_date": "2026-05-21",
  "status_filter": "open"
}
Expected: 
  - success: true
  - work_packages_by_project: array
  - Each project has work_packages list
  - Tasks sorted by due_date
```

#### TC2.2: Query This Week's Tasks
```
Payload: {
  "start_date": "2026-05-19",
  "end_date": "2026-05-25",
  "status_filter": "open",
  "group_by_project": true
}
Expected:
  - Total work packages count matches sum of all projects
  - Projects properly grouped
  - No duplicates in results
```

#### TC2.3: Filter by Specific Project IDs
```
Payload: {
  "start_date": "2026-05-19",
  "end_date": "2026-05-25",
  "project_ids": [5, 2],
  "status_filter": "open"
}
Expected:
  - Only tasks from projects 5 and 2
  - Other projects excluded
  - Correct task count
```

#### TC2.4: Invalid Date Format
```
Payload: {
  "start_date": "21-05-2026",  # Wrong format
  "end_date": "2026-05-25"
}
Expected:
  - success: false
  - error: "Start date must be in YYYY-MM-DD format"
```

#### TC2.5: Date Range Validation
```
Payload: {
  "start_date": "2026-05-25",
  "end_date": "2026-05-19"  # End before start
}
Expected:
  - Either empty results or sorted correctly
  - No error thrown
```

### Test Suite 3: CLI Wrapper Commands

#### TC3.1: List Projects
```
Command: python nanoclaw_skill/openproject_cli.py list_projects
Expected:
  - success: true
  - projects: [array of project objects]
  - Each project has: id, name, identifier, url
  - At least 2 test projects listed
```

#### TC3.2: Create Project
```
Command: python nanoclaw_skill/openproject_cli.py create_project \
  --name "CLI Test Project" \
  --description "Created by automated test"
Expected:
  - success: true
  - project_id: positive integer
  - project_name: "CLI Test Project"
  - Verify project appears in list_projects result
```

#### TC3.3: Create Task
```
Command: python nanoclaw_skill/openproject_cli.py create_task \
  --project_id 5 \
  --subject "Integration Test Task" \
  --description "Testing CLI task creation" \
  --due_date "2026-05-22" \
  --estimated_hours 2
Expected:
  - success: true
  - work_package_id: positive integer
  - subject: "Integration Test Task"
  - Verify task appears in project via OpenProject UI
```

#### TC3.4: Create Task with Assignee
```
Command: python nanoclaw_skill/openproject_cli.py create_task \
  --project_id 5 \
  --subject "Assigned Test Task" \
  --assignee_email "george@example.com" \
  --due_date "2026-05-23"
Expected:
  - Task created successfully
  - Assigned to george@example.com
  - Verify in OpenProject UI
```

#### TC3.5: Get Tasks by Date (Today)
```
Command: python nanoclaw_skill/openproject_cli.py get_tasks_by_date \
  --date_range "today" \
  --status open
Expected:
  - success: true
  - work_packages_by_project: grouped by project
  - Only today's tasks included
  - Grouped output contains all necessary fields
```

#### TC3.6: Get Tasks by Date (Date Range)
```
Command: python nanoclaw_skill/openproject_cli.py get_tasks_by_date \
  --date_range "today to +2" \
  --projects "all" \
  --status open
Expected:
  - Success with 3-day range (today + 2 days)
  - Tasks from all projects included
  - Each task has due_date within range
```

#### TC3.7: Get Tasks by Date (Specific Projects)
```
Command: python nanoclaw_skill/openproject_cli.py get_tasks_by_date \
  --date_range "this week" \
  --projects "5,2"
Expected:
  - Only projects 5 and 2 in results
  - Other projects excluded
  - Results properly grouped
```

#### TC3.8: Update Task
```
Command: python nanoclaw_skill/openproject_cli.py update_task \
  --task_id {created_task_id} \
  --status "In Progress" \
  --due_date "2026-05-25"
Expected:
  - success: true
  - updated_fields include status and due_date
  - Verify change in OpenProject UI
```

#### TC3.9: Create Task Dependency
```
Command: python nanoclaw_skill/openproject_cli.py create_dependency \
  --from_task_id {task1_id} \
  --to_task_id {task2_id} \
  --relation_type "follows" \
  --description "Task2 depends on Task1"
Expected:
  - success: true
  - relation_id: positive integer
  - Verify dependency in OpenProject Gantt chart
```

#### TC3.10: Get Project Summary
```
Command: python nanoclaw_skill/openproject_cli.py get_project_summary \
  --project_id 5
Expected:
  - success: true
  - total_tasks: positive integer
  - tasks_by_status: object with status counts
  - overdue_tasks: count
  - tasks_due_this_week: count
```

#### TC3.11: Get Project Team
```
Command: python nanoclaw_skill/openproject_cli.py get_project_team \
  --project_id 5
Expected:
  - success: true
  - members: array of team members
  - Each member has: user_id, email, name, role
```

#### TC3.12: Invalid Command Arguments
```
Command: python nanoclaw_skill/openproject_cli.py create_task \
  --project_id abc  # Invalid: not a number
Expected:
  - Error message indicating invalid argument
  - Graceful failure
```

### Test Suite 4: Date Helper Utilities

#### TC4.1: Date Range Parsing - "today"
```python
from src.utils.date_helpers import normalize_date_range
start, end = normalize_date_range("today")
Expected:
  - start == end == "2026-05-21" (today's date)
```

#### TC4.2: Date Range Parsing - "today to +2"
```python
start, end = normalize_date_range("today to +2")
Expected:
  - start == "2026-05-21"
  - end == "2026-05-23"
  - Format: YYYY-MM-DD
```

#### TC4.3: Date Range Parsing - "this week"
```python
start, end = normalize_date_range("this week")
Expected:
  - start: Monday of current week
  - end: Sunday of current week
  - 7 days apart (or 6 for current day logic)
```

#### TC4.4: Date Range Parsing - "next week"
```python
start, end = normalize_date_range("next week")
Expected:
  - start: Monday of next week
  - end: Sunday of next week
```

#### TC4.5: Date Range Parsing - Explicit Range
```python
start, end = normalize_date_range("2026-05-21 to 2026-05-28")
Expected:
  - start == "2026-05-21"
  - end == "2026-05-28"
```

#### TC4.6: Date Range Parsing - Invalid Format
```python
try:
    normalize_date_range("invalid date")
except ValueError as e:
    Expected: ValueError with helpful message
```

#### TC4.7: Valid Date Format Check
```python
from src.utils.date_helpers import is_valid_date_format
Expected:
  - is_valid_date_format("2026-05-21") == True
  - is_valid_date_format("21-05-2026") == False
  - is_valid_date_format("2026/05/21") == False
```

#### TC4.8: Business Days Calculation
```python
from src.utils.date_helpers import get_business_days_between
# May 21-25, 2026 (Wed-Sun): 3 business days (Wed, Thu, Fri)
days = get_business_days_between("2026-05-21", "2026-05-25")
Expected: days == 3 (skips Sat, Sun)
```

### Test Suite 5: Multi-Project Integration

#### TC5.1: Create Tasks in Multiple Projects
```
Create:
  - Task A in HP Server Build (project 5)
  - Task B in Nutrition Tracker (project 2)
  - Task C in Other Project (project 999)
All with due date: 2026-05-22

Query: get_tasks_by_date --date_range "2026-05-22"
Expected:
  - All 3 tasks returned
  - Grouped by project
  - Project names correct
  - Task subjects correct
```

#### TC5.2: Cross-Project Dependencies
```
Create:
  - Task A in project 5 with due date 2026-05-21
  - Task B in project 2 with due date 2026-05-22
  - Dependency: B follows A

Expected:
  - Dependency created successfully
  - Gantt chart shows relationship
  - No errors for cross-project links
```

#### TC5.3: Overdue Task Aggregation
```
Create tasks with due date: 2026-05-19 (2 days in past)
Query: get_tasks_by_date --date_range "2026-05-19 to 2026-05-19"
Expected:
  - Overdue tasks returned
  - Status shown in results
  - Aggregated across projects
```

### Test Suite 6: Error Handling & Edge Cases

#### TC6.1: Connection Timeout
```
Stop MCP server
Command: openproject_cli.py list_projects
Expected:
  - Graceful error message
  - No unhandled exception
  - Suggests checking server connection
```

#### TC6.2: Invalid OpenProject Response
```
Mock invalid API response
Expected:
  - Proper error handling
  - User-friendly error message
  - No JSON decode errors
```

#### TC6.3: Empty Result Set
```
Query date range with no tasks
Expected:
  - success: true
  - Empty work_packages array
  - No error thrown
```

#### TC6.4: Missing Required Arguments
```
Command: openproject_cli.py create_task --project_id 5
(Missing: --subject)
Expected:
  - Error: subject is required
  - Usage help displayed
```

#### TC6.5: Large Result Set
```
Create 100+ tasks in a project
Query: get_tasks_by_date --date_range "this month"
Expected:
  - All tasks returned
  - Proper grouping by project
  - No timeouts or truncation
```

---

## Performance Baselines

Document baseline performance metrics:

| Operation | Target | Actual |
|-----------|--------|--------|
| list_projects | < 1s | _____ |
| get_tasks_by_date (10 tasks) | < 1s | _____ |
| get_tasks_by_date (100 tasks) | < 2s | _____ |
| create_task | < 1s | _____ |
| create_dependency | < 1s | _____ |
| get_project_summary | < 1s | _____ |

---

## Test Execution Checklist

### Pre-Test
- [ ] MCP server running on port 8085
- [ ] OpenProject instance running on port 3000
- [ ] Python 3.8+ with httpx installed
- [ ] Test projects created
- [ ] No network connectivity issues
- [ ] Sufficient disk space for test data

### Test Suite 1: MCP Health
- [ ] TC1.1: Health check passes
- [ ] TC1.2: OpenProject connection successful

### Test Suite 2: Date Range Queries
- [ ] TC2.1: Today's tasks query works
- [ ] TC2.2: Week range query works
- [ ] TC2.3: Project filtering works
- [ ] TC2.4: Invalid date rejected
- [ ] TC2.5: Date validation correct

### Test Suite 3: CLI Commands
- [ ] TC3.1: list_projects works
- [ ] TC3.2: create_project works
- [ ] TC3.3: create_task works
- [ ] TC3.4: Task assignment works
- [ ] TC3.5: get_tasks_by_date works
- [ ] TC3.6: Date range parsing works
- [ ] TC3.7: Project filtering works
- [ ] TC3.8: update_task works
- [ ] TC3.9: create_dependency works
- [ ] TC3.10: get_project_summary works
- [ ] TC3.11: get_project_team works
- [ ] TC3.12: Error handling works

### Test Suite 4: Date Helpers
- [ ] TC4.1: "today" parsing
- [ ] TC4.2: "today to +N" parsing
- [ ] TC4.3: "this week" parsing
- [ ] TC4.4: "next week" parsing
- [ ] TC4.5: Explicit range parsing
- [ ] TC4.6: Invalid format error
- [ ] TC4.7: Date validation
- [ ] TC4.8: Business days calculation

### Test Suite 5: Multi-Project
- [ ] TC5.1: Multi-project task creation
- [ ] TC5.2: Cross-project dependencies
- [ ] TC5.3: Overdue aggregation

### Test Suite 6: Error Handling
- [ ] TC6.1: Connection timeout handling
- [ ] TC6.2: Invalid response handling
- [ ] TC6.3: Empty result handling
- [ ] TC6.4: Missing arguments error
- [ ] TC6.5: Large result set handling

### Post-Test
- [ ] All test data cleaned up
- [ ] MCP server stable
- [ ] OpenProject instance stable
- [ ] Performance baselines recorded
- [ ] Test results documented

---

## Known Limitations & Caveats

1. **Windows Line Endings**: Git may show CRLF warnings on Windows - expected
2. **Timezone Handling**: Date parsing uses system timezone
3. **Permission-Based Filtering**: OpenProject respects user permissions
4. **API Rate Limiting**: High volume queries may be throttled by OpenProject
5. **Concurrent Requests**: MCP server can handle multiple requests but not unlimited

---

## Test Result Summary

**Date Tested**: _______________
**Tester**: _______________
**Version**: 1.0.0

### Results

| Suite | Pass | Fail | Notes |
|-------|------|------|-------|
| MCP Health (2) | ___ | ___ | |
| Date Queries (5) | ___ | ___ | |
| CLI Commands (12) | ___ | ___ | |
| Date Helpers (8) | ___ | ___ | |
| Multi-Project (3) | ___ | ___ | |
| Error Handling (5) | ___ | ___ | |
| **TOTAL** | ___ | ___ | |

**Pass Rate**: ____/35 tests = ____%

### Issues Found

1. Issue: _______________
   - Severity: High / Medium / Low
   - Reproduction: _______________
   - Fix: _______________

2. Issue: _______________
   - ...

### Sign-Off

- [ ] All critical tests passing
- [ ] Performance acceptable
- [ ] Ready for NanoClaw integration
- [ ] Ready for production deployment

**Signed Off By**: _______________
**Date**: _______________

---

## Next Steps

After successful testing:

1. Deploy MCP server to production
2. Register skill with NanoClaw
3. Test end-to-end with NanoClaw agent
4. Monitor for issues in production
5. Plan post-MVP enhancements

