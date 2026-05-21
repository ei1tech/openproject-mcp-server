@echo off
REM OpenProject Restore Script from P: Drive
REM Run this script to restore OpenProject data from P: drive backup

echo 🔄 Starting OpenProject restore from P: drive...

REM Check if P: drive exists
if not exist "P:\" (
    echo ❌ P: drive not accessible
    exit /b 1
)

REM List available backups
echo 📋 Available backups:
dir "P:\OpenProject\backups\" /AD /B

echo.
set /p BACKUP_FOLDER="Enter backup folder name (e.g., backup_20240831_181500): "

set RESTORE_DIR=P:\OpenProject\backups\%BACKUP_FOLDER%

if not exist "%RESTORE_DIR%" (
    echo ❌ Backup directory does not exist: %RESTORE_DIR%
    pause
    exit /b 1
)

echo ⚠️ WARNING: This will replace all current OpenProject data!
set /p CONFIRM="Are you sure? (type 'YES' to continue): "
if not "%CONFIRM%"=="YES" (
    echo ❌ Restore cancelled
    pause
    exit /b 0
)

REM Stop OpenProject
echo 🛑 Stopping OpenProject...
docker compose down

REM Backup current data (just in case)
echo 💾 Creating safety backup of current data...
if exist "data\" (
    for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
    set SAFETY_TIMESTAMP=%datetime:~0,8%_%datetime:~8,6%
    mkdir "data_backup_before_restore_%SAFETY_TIMESTAMP%"
    xcopy /E /I /Y "data" "data_backup_before_restore_%SAFETY_TIMESTAMP%\"
)

REM Remove current data
echo 🗑️ Removing current data...
if exist "data\" rmdir /S /Q "data\"

REM Restore from backup
echo 📥 Restoring PostgreSQL data...
xcopy /E /I /Y "%RESTORE_DIR%\pgdata" "data\pgdata\"

echo 📎 Restoring assets data...
xcopy /E /I /Y "%RESTORE_DIR%\assets" "data\assets\"

echo ⚙️ Restoring configuration...
if exist "%RESTORE_DIR%\docker-compose.yml" copy "%RESTORE_DIR%\docker-compose.yml" "." /Y
if exist "%RESTORE_DIR%\.env" copy "%RESTORE_DIR%\.env" "." /Y

REM Start OpenProject
echo ▶️ Starting OpenProject...
docker compose up -d openproject

echo ✅ Restore completed successfully!
echo 🌐 OpenProject should be available at: http://openproject.home:9090

pause