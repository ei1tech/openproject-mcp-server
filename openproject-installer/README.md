# OpenProject Docker Installation with Persistent Storage

A complete OpenProject deployment solution with automatic data persistence, proxy integration, and backup capabilities.

## 🚀 Quick Start

### Prerequisites
- Docker Desktop installed and running
- nginx-proxy container running on port 80 (for openproject.home access)
- P: drive accessible (for backups)

### Initial Setup
1. Navigate to the installation directory:
   ```cmd
   cd openproject-installer
   ```

2. Create/edit the `.env` file:
   ```bash
   OPENPROJECT_SECRET_KEY_BASE=your-secret-key-here-change-this-in-production
   ```

3. Deploy OpenProject:
   ```cmd
   # Windows
   deploy-openproject.bat
   
   # Linux/macOS  
   ./deploy-openproject.sh
   ```

4. Access OpenProject at: http://openproject.home
   - Default username: `admin`
   - Default password: `admin`

## 📁 Directory Structure

```
openproject-installer/
├── docker-compose.yml          # Container orchestration
├── deploy-openproject.bat      # Windows deployment script
├── deploy-openproject.sh       # Linux/macOS deployment script
├── backup-to-p-drive.bat      # Backup script
├── restore-from-p-drive.bat   # Restore script  
├── .env                       # Environment variables
├── data/                      # Persistent data storage
│   ├── assets/               # File uploads, attachments
│   └── pgdata/               # PostgreSQL database
└── README.md                 # This documentation
```

## 🔧 Key Technical Details

### Container Configuration
- **Image**: `openproject/openproject:14`
- **Container Name**: `openproject`
- **Internal Port**: 80
- **External Port**: 9090
- **Networks**: 
  - `openproject-installer_openproject-network` (internal)
  - `bridge` (for nginx-proxy discovery)

### Environment Variables
```yaml
VIRTUAL_HOST: openproject.home          # Proxy hostname
VIRTUAL_PORT: 80                        # Internal container port
OPENPROJECT_HOST__NAME: openproject.home
OPENPROJECT_HTTPS: false
OPENPROJECT_SECRET_KEY_BASE: <your-key>
```

### Data Persistence
- **Method**: Bind mounts (not Docker volumes)
- **Database**: `./data/pgdata` → `/var/openproject/pgdata`
- **Assets**: `./data/assets` → `/var/openproject/assets`
- **Benefits**: 
  - Direct file access
  - Easy backup/restore
  - Survives container deletion
  - Cross-platform compatible

### Network Architecture
```
Internet → nginx-proxy:80 → openproject:80 (internal)
                ↓
         openproject.home → 172.17.0.x:80
```

## 🔄 Deployment Process

### Automated Deployment
The deployment scripts handle the complete deployment lifecycle:

1. **Image Management**
   - Pulls latest OpenProject image
   - Handles version updates automatically

2. **Container Lifecycle**
   - Gracefully stops existing container
   - Removes old container (preserves data)
   - Creates new container with fresh image

3. **Network Integration**
   - Connects container to internal network
   - Connects to bridge network for proxy discovery
   - Restarts nginx-proxy for container discovery

4. **Health Monitoring**
   - Waits for container health checks
   - Validates service availability
   - Reports deployment status

### Manual Deployment
```cmd
# Stop services
docker compose down

# Update images
docker compose pull

# Start services
docker compose up -d openproject

# Connect to proxy network
docker network connect bridge openproject

# Restart proxy for discovery
docker restart nginx-proxy
```

## 💾 Backup Process

### Automated Backup to P: Drive

Run the backup script:
```cmd
backup-to-p-drive.bat
```

**What it does:**
1. Stops OpenProject for consistent backup
2. Creates timestamped backup directory on P: drive
3. Copies PostgreSQL data (`data/pgdata/`)
4. Copies assets data (`data/assets/`)
5. Backs up configuration files (`.env`, `docker-compose.yml`)
6. Restarts OpenProject
7. Reports backup size and location

**Backup Location:**
```
P:\OpenProject\backups\backup_YYYYMMDD_HHMMSS\
├── pgdata/               # Database backup
├── assets/               # Assets backup
├── docker-compose.yml    # Configuration backup
└── .env                  # Environment backup
```

### Manual Backup
```cmd
# Stop OpenProject
docker compose stop openproject

# Create backup directory
mkdir "P:\OpenProject\backups\manual_backup_%DATE%"

# Copy data
xcopy /E /I "data\*" "P:\OpenProject\backups\manual_backup_%DATE%\"

# Restart OpenProject
docker compose up -d openproject
```

## 🔄 Restore Process

### Automated Restore from P: Drive

Run the restore script:
```cmd
restore-from-p-drive.bat
```

**Interactive Process:**
1. Lists available backups on P: drive
2. Prompts for backup selection
3. Confirms restore operation (destructive)
4. Creates safety backup of current data
5. Stops OpenProject
6. Restores data from selected backup
7. Restarts OpenProject

### Manual Restore
```cmd
# Stop OpenProject
docker compose down

# Backup current data (safety)
move data data_backup_%DATE%

# Restore from backup
xcopy /E /I "P:\OpenProject\backups\backup_YYYYMMDD_HHMMSS\pgdata" "data\pgdata\"
xcopy /E /I "P:\OpenProject\backups\backup_YYYYMMDD_HHMMSS\assets" "data\assets\"

# Start OpenProject
docker compose up -d openproject
docker network connect bridge openproject
```

## 🛠️ Maintenance

### Regular Operations

**Update OpenProject:**
```cmd
deploy-openproject.bat
```

**View Logs:**
```cmd
docker compose logs -f openproject
```

**Check Status:**
```cmd
docker compose ps
```

**Restart Service:**
```cmd
docker compose restart openproject
docker network connect bridge openproject
```

### Health Monitoring
- **Health Check**: Built-in container health monitoring
- **Access Check**: `curl -I http://openproject.home`
- **Direct Access**: `curl -I http://localhost:9090`

### Data Verification
```cmd
# Check data directories
dir data\pgdata
dir data\assets

# Check database size
docker exec openproject du -sh /var/openproject/pgdata

# Check assets size  
docker exec openproject du -sh /var/openproject/assets
```

## 🔒 Security Considerations

### Required Changes for Production
1. **Change default admin password** immediately after first login
2. **Update SECRET_KEY_BASE** in `.env` file:
   ```bash
   OPENPROJECT_SECRET_KEY_BASE=$(openssl rand -hex 64)
   ```
3. **Enable HTTPS** in production environments
4. **Regular backups** to secure off-site location
5. **Monitor access logs** and user activity

### Network Security
- OpenProject runs on internal networks
- Only nginx-proxy exposes port 80
- Direct access available on localhost:9090 for troubleshooting

## 🐛 Troubleshooting

### Common Issues

**Proxy not working (502 Bad Gateway):**
```cmd
# Reconnect to bridge network
docker network connect bridge openproject
docker restart nginx-proxy
```

**Container won't start:**
```cmd
# Check logs
docker compose logs openproject

# Check disk space
df -h

# Verify data directory permissions
ls -la data/
```

**Data not persisting:**
```cmd
# Verify volume mounts
docker inspect openproject | grep -A 10 "Mounts"

# Check data directories exist
ls -la data/pgdata data/assets
```

**Performance issues:**
```cmd
# Check resource usage
docker stats openproject

# Check database size
docker exec openproject psql -U openproject -c "\l+"
```

### Recovery Procedures

**Complete data corruption:**
1. Stop OpenProject: `docker compose down`
2. Remove corrupted data: `rmdir /S data`  
3. Restore from backup: `restore-from-p-drive.bat`

**Container corruption:**
1. Remove container: `docker rm -f openproject`
2. Remove image: `docker rmi openproject/openproject:14`
3. Redeploy: `deploy-openproject.bat`

## 📞 Support

### Log Collection
```cmd
# Container logs
docker compose logs openproject > openproject-logs.txt

# System info
docker version > system-info.txt
docker compose version >> system-info.txt

# Container info
docker inspect openproject > container-info.txt
```

### Useful Commands
```cmd
# Enter container shell
docker exec -it openproject bash

# Database access
docker exec -it openproject psql -U openproject

# File system access
docker exec -it openproject ls -la /var/openproject/
```

---

## 📋 File Manifest

- `docker-compose.yml` - Container orchestration configuration
- `deploy-openproject.bat/sh` - Automated deployment scripts  
- `backup-to-p-drive.bat` - Automated backup to P: drive
- `restore-from-p-drive.bat` - Automated restore from P: drive
- `.env` - Environment variables (create manually)
- `data/` - Persistent data directory (auto-created)
- `README.md` - This documentation

**Deployment verified:** ✅ Data persistence confirmed across container rebuilds