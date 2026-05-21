# OpenProject MCP Server

A Model Context Protocol (MCP) server that enables AI assistants to interact with OpenProject installations. Create projects, manage work packages, assign team members, and generate Gantt charts through natural language commands.

## Features

- **Project Management**: Create and manage OpenProject projects
- **Work Package Operations**: Create, update, and assign work packages with dates
- **Dependency Management**: Create relationships between work packages for Gantt charts
- **User Management**: Find and assign users by email address
- **Team Collaboration**: Manage project members and their roles
- **Dynamic Configuration**: Automatically loads work package types, statuses, and priorities
- **Comprehensive Reporting**: Project status reports and team workload analysis

## Installation

### Prerequisites

- OpenProject instance (local or cloud)
- API key from your OpenProject profile
- Python 3.8+ or Docker

### Method 1: Docker (Recommended)

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd openproject-mcp-server
   ```

2. **Configure environment**:
   ```bash
   cp env.example .env
   # Edit .env with your OpenProject details
   ```

3. **Deploy with Docker**:
   ```bash
   ./scripts/deploy.sh deploy 39127
   ```

### Method 2: Python

1. **Clone and setup**:
   ```bash
   git clone <repository-url>
   cd openproject-mcp-server
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure environment**:
   ```bash
   cp env.example .env
   # Edit .env with your OpenProject details
   ```

3. **Test configuration**:
   ```bash
   python3 scripts/test_mvp.py
   ```

## Configuration

Create a `.env` file with your OpenProject details:

```env
# OpenProject Instance URL (include protocol)
OPENPROJECT_URL=http://localhost:8080

# OpenProject API Key (from your user profile)
OPENPROJECT_API_KEY=your_40_character_api_key_here

# MCP Server Configuration (optional)
MCP_HOST=localhost
MCP_PORT=39127
MCP_LOG_LEVEL=INFO
```

### Getting your OpenProject API Key

1. Login to your OpenProject instance
2. Go to **My Account** → **Access Tokens**
3. Click **+ New token**
4. Enter a name (e.g., "MCP Server")
5. Copy the generated 40-character token

## Usage

### Starting the Server

**Docker:**
```bash
./scripts/deploy.sh deploy 39127
```

**Python:**
```bash
python3 scripts/run_server.py
```

### MCP Client Configuration

#### Claude Desktop

Add to your `claude_desktop_config.json`:

**For Docker deployment:**
```json
{
  "mcpServers": {
    "openproject": {
      "transport": "sse",
      "url": "http://localhost:39127/sse"
    }
  }
}
```

**For local Python:**
```json
{
  "mcpServers": {
    "openproject": {
      "command": "python3",
      "args": ["/full/path/to/openproject-mcp-server/scripts/run_server.py"],
      "env": {
        "OPENPROJECT_URL": "http://localhost:8080",
        "OPENPROJECT_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

#### Other MCP Clients

Use the SSE transport URL: `http://localhost:39127/sse`

## Available Tools

### Project Management
- `create_project` - Create new projects
- `get_projects` - List all projects
- `get_project_summary` - Get detailed project overview
- `get_project_members` - List project members and roles

### Work Package Management
- `create_work_package` - Create work packages with dates and assignments
- `get_work_packages` - List work packages for a project
- `update_work_package` - Update existing work packages
- `assign_work_package_by_email` - Assign work packages using email addresses

### Dependency Management
- `create_work_package_dependency` - Create relationships for Gantt charts
- `get_work_package_relations` - List dependencies for a work package
- `delete_work_package_relation` - Remove relationships

### User Management
- `get_users` - List users with optional email filtering

### Configuration
- `get_work_package_types` - List available work package types
- `get_work_package_statuses` - List available statuses
- `get_priorities` - List available priorities

## Example Commands

Once integrated with an AI assistant, you can use natural language:

**Create a project with team:**
```
Create a project called "Website Redesign" and add john@example.com and sarah@example.com to the team.
```

**Create work packages with dependencies:**
```
In project ID 5, create:
1. "Requirements Analysis" from 2024-01-15 to 2024-01-20, assign to john@example.com
2. "UI Design" from 2024-01-21 to 2024-02-05, assign to sarah@example.com
3. "Development" from 2024-02-06 to 2024-02-28

Make UI Design depend on Requirements Analysis, and Development depend on UI Design.
```

**Get project status:**
```
Show me a summary of project ID 5 including all work packages and team assignments.
```

## Resources

The server provides read-only resources for browsing OpenProject data:

- `openproject://projects` - List all projects
- `openproject://project/{project_id}` - Get specific project details
- `openproject://work-packages/{project_id}` - Get work packages for a project
- `openproject://work-package/{work_package_id}` - Get specific work package details

## Docker Management

### Deployment Commands
```bash
# Deploy on port 39127 (recommended)
./scripts/deploy.sh deploy 39127

# View logs
./scripts/deploy.sh logs

# Check status
./scripts/deploy.sh status

# Stop server
./scripts/deploy.sh stop

# Restart server
./scripts/deploy.sh restart

# Clean up (remove container and image)
./scripts/deploy.sh clean
```

### Manual Docker Commands
```bash
# Build image
docker build -t openproject-mcp-server .

# Run container
docker run -d \
  --name openproject-mcp-server \
  --env-file .env \
  -p 39127:39127 \
  -v ./logs:/app/logs \
  -v ./data:/app/data \
  --restart unless-stopped \
  openproject-mcp-server
```

## Troubleshooting

### Connection Issues
- Verify OpenProject URL is accessible
- Check API key is correct (40 characters)
- Ensure OpenProject API is enabled

### Permission Issues
- Verify your user has project creation permissions
- Check work package creation permissions in target project

### Date Format Issues
- Use YYYY-MM-DD format for all dates
- Ensure due_date is after start_date

### Docker Issues
```bash
# Check container status
docker ps

# View container logs
docker logs openproject-mcp-server

# Test API endpoint
curl http://localhost:39127/sse
```

## Testing

```bash
# Test basic connection
python3 scripts/test_mvp.py

# Run comprehensive tests
python3 tests/run_tests.py

# Run with pytest
pip install -r requirements-test.txt
python3 -m pytest tests/ -v
```

## Development

### Project Structure
```
openproject-mcp-server/
├── src/                    # Source code
├── scripts/               # Deployment and test scripts
├── tests/                 # Test suite
├── docker-compose.yml     # Docker configuration
├── Dockerfile            # Container build instructions
└── requirements.txt      # Python dependencies
```

### Running Tests
```bash
# Install test dependencies
pip install -r requirements-test.txt

# Run all tests
python3 -m pytest tests/ -v

# Run with coverage
python3 -m pytest --cov=src --cov-report=html tests/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

[License information]

## Support

For issues and questions:
1. Check the troubleshooting section above
2. Review container logs: `docker logs openproject-mcp-server`
3. Test your OpenProject API connection
4. Verify your configuration in `.env` file