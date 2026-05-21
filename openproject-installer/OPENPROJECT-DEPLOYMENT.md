# OpenProject Deployment with Persistent Storage

This specification provides a complete solution for deploying OpenProject with persistent storage, automated updates, and data preservation.

## Overview

- **Port**: 9090 (mapped to container port 80)
- **URL**: http://openproject.home:9090
- **Data Persistence**: Full persistence using Docker volumes
- **Updates**: Automated deployment script that pulls latest images without data loss

## Files

- `docker-compose.yml` - Container orchestration with persistent volumes
- `deploy-openproject.sh` - Linux/macOS deployment script
- `deploy-openproject.bat` - Windows deployment script

## Quick Start

### 1. Environment Setup

Create a `.env` file with required variables:

```bash
OPENPROJECT_SECRET_KEY_BASE=your-secret-key-here
OPENPROJECT_URL=http://openproject.home:9090
OPENPROJECT_API_KEY=your-api-key-here
MCP_HOST=0.0.0.0
MCP_PORT=39127
MCP_LOG_LEVEL=INFO
```

### 2. Initial Deployment

**Linux/macOS:**
```bash
chmod +x deploy-openproject.sh
./deploy-openproject.sh
```

**Windows:**
```cmd
deploy-openproject.bat
```

### 3. Access OpenProject

Navigate to: http://openproject.home:9090

Default credentials:
- Username: `admin`
- Password: `admin`

## Persistent Storage

### Volumes Created

- `openproject_data` - File uploads, attachments, avatars
- `openproject_pgdata` - PostgreSQL database (users, projects, work packages)

### Volume Locations

Docker stores named volumes in:
- **Linux**: `/var/lib/docker/volumes/`
- **Windows**: `\\wsl$\docker-desktop-data\data\docker\volumes\`

## Deployment Process

The deployment script:

1. **Pulls latest image** - Gets `openproject/community:latest`
2. **Stops existing container** - Graceful shutdown
3. **Removes old container** - Keeps volumes intact
4. **Starts new container** - Uses latest image with existing data
5. **Health check** - Waits for service to be ready

## Data Persistence Guarantee

✅ **Data is preserved across:**
- Container restarts
- Image updates
- Host reboots
- Script deployments

❌ **Data is lost only if:**
- Volumes are manually deleted
- `docker volume rm` commands are used
- Host filesystem corruption

## Manual Commands

### View running services
```bash
docker compose ps
```

### View logs
```bash
docker compose logs -f openproject
```

### Stop service
```bash
docker compose stop openproject
```

### Start service
```bash
docker compose up -d openproject
```

### Backup volumes
```bash
# Create backup
docker run --rm -v openproject_data:/source -v $(pwd):/backup alpine tar czf /backup/openproject_data.tar.gz -C /source .
docker run --rm -v openproject_pgdata:/source -v $(pwd):/backup alpine tar czf /backup/openproject_pgdata.tar.gz -C /source .
```

### Restore volumes
```bash
# Restore backup (stop OpenProject first)
docker compose stop openproject
docker run --rm -v openproject_data:/target -v $(pwd):/backup alpine tar xzf /backup/openproject_data.tar.gz -C /target
docker run --rm -v openproject_pgdata:/target -v $(pwd):/backup alpine tar xzf /backup/openproject_pgdata.tar.gz -C /target
docker compose up -d openproject
```

## Troubleshooting

### Service won't start
```bash
# Check logs
docker compose logs openproject

# Check container status
docker compose ps
```

### Health check failing
The container includes a built-in health check that tests the web interface. If failing:
1. Check if port 9090 is available
2. Verify network connectivity
3. Check system resources (memory/disk)

### Data appears missing
1. Verify volumes exist: `docker volume ls | grep openproject`
2. Check volume contents: `docker run --rm -v openproject_data:/data alpine ls -la /data`
3. Ensure container is using correct volumes

## Security Notes

- Change default admin password immediately
- Use strong `OPENPROJECT_SECRET_KEY_BASE`
- Consider using HTTPS in production
- Regularly backup volumes

## Updating OpenProject

Simply run the deployment script again - it automatically:
1. Pulls the latest image
2. Preserves all existing data
3. Restarts with new version

No manual intervention required for updates.