@echo off
REM OpenProject Deployment Script for Windows
REM Automatically pulls latest image while preserving data

echo 🚀 Starting OpenProject deployment...

REM Check if docker is available
docker version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not installed or not running
    exit /b 1
)

REM Check if docker compose is available
docker compose version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker Compose is not available
    exit /b 1
)

echo 📦 Using: docker compose

REM Check if .env file exists
if not exist ".env" (
    echo ⚠️  .env file not found. Please create one with required environment variables.
    echo    Example variables needed:
    echo    OPENPROJECT_SECRET_KEY_BASE=your-secret-key-here
    exit /b 1
)

REM Pull latest images
echo 📥 Pulling latest OpenProject image...
docker compose pull openproject

REM Stop the service gracefully (if running)
echo 🛑 Stopping existing OpenProject service...
docker compose stop openproject 2>nul

REM Remove the old container (keeps volumes intact)
echo 🗑️  Removing old container (data will be preserved)...
docker compose rm -f openproject 2>nul

REM Start the service with new image
echo ▶️  Starting OpenProject with latest image...
docker compose up -d openproject

REM Connect to bridge network for nginx-proxy discovery
echo 🔗 Connecting OpenProject to bridge network for proxy discovery...
docker network connect bridge openproject 2>nul || echo Already connected to bridge network

REM Restart nginx-proxy to discover the new container
echo 🔄 Restarting nginx-proxy for container discovery...
docker restart nginx-proxy 2>nul || echo nginx-proxy not found - skipping restart

REM Wait for healthcheck
echo 🏥 Waiting for OpenProject to be healthy...
set timeout=30
set counter=0

:healthcheck_loop
if %counter% geq %timeout% (
    goto timeout_error
)

docker compose ps openproject | findstr "healthy" >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ OpenProject is healthy and ready!
    echo 🌐 Access OpenProject at: http://openproject.home:9090
    goto success
)

docker compose ps openproject | findstr "unhealthy" >nul 2>&1
if %errorlevel% equ 0 (
    echo ❌ OpenProject health check failed
    echo 📋 Showing logs:
    docker compose logs --tail=50 openproject
    exit /b 1
)

echo ⏳ Waiting for OpenProject to start... (%counter%/%timeout% attempts)
timeout /t 10 >nul
set /a counter+=1
goto healthcheck_loop

:timeout_error
echo ⏰ Timeout waiting for OpenProject to become healthy
echo 📋 Showing logs:
docker compose logs --tail=50 openproject
exit /b 1

:success
echo.
echo 🎉 OpenProject deployment completed successfully!
echo 📊 Container status:
docker compose ps openproject

echo.
echo 💾 Volume information:
docker volume ls | findstr openproject || echo No OpenProject volumes found (this might be normal for first run)

pause