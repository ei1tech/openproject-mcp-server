@echo off
REM OpenProject Backup Script to P: Drive
REM Run this script to backup OpenProject data to P: drive

echo 🔄 Starting OpenProject backup to P: drive...

REM Check if P: drive exists
if not exist "P:\" (
    echo ❌ P: drive not accessible
    exit /b 1
)

REM Create backup directories on P: drive
if not exist "P:\OpenProject\" mkdir "P:\OpenProject\"
if not exist "P:\OpenProject\backups\" mkdir "P:\OpenProject\backups\"

REM Generate timestamp for backup
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
set TIMESTAMP=%datetime:~0,8%_%datetime:~8,6%

set BACKUP_DIR=P:\OpenProject\backups\backup_%TIMESTAMP%

echo 📁 Creating backup directory: %BACKUP_DIR%
mkdir "%BACKUP_DIR%"

REM Stop OpenProject for consistent backup
echo 🛑 Stopping OpenProject for backup...
docker compose stop openproject

REM Backup PostgreSQL data
echo 💾 Backing up PostgreSQL data...
xcopy /E /I /Y "data\pgdata" "%BACKUP_DIR%\pgdata\"

REM Backup assets data
echo 📎 Backing up assets data...
xcopy /E /I /Y "data\assets" "%BACKUP_DIR%\assets\"

REM Backup configuration files
echo ⚙️ Backing up configuration...
copy "docker-compose.yml" "%BACKUP_DIR%\"
copy ".env" "%BACKUP_DIR%\" 2>nul

REM Restart OpenProject
echo ▶️ Restarting OpenProject...
docker compose up -d openproject

echo ✅ Backup completed successfully!
echo 📍 Backup location: %BACKUP_DIR%
echo 📊 Backup size:
dir "%BACKUP_DIR%" /s

pause