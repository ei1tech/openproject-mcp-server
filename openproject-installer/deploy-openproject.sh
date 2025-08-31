#!/bin/bash

# OpenProject Deployment Script
# Automatically pulls latest image while preserving data

set -e

echo "🚀 Starting OpenProject deployment..."

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null && ! command -v docker compose &> /dev/null; then
    echo "❌ Docker Compose is not installed"
    exit 1
fi

# Use docker compose or docker-compose depending on what's available
DOCKER_COMPOSE_CMD="docker compose"
if ! command -v docker &> /dev/null || ! docker compose version &> /dev/null 2>&1; then
    if command -v docker-compose &> /dev/null; then
        DOCKER_COMPOSE_CMD="docker-compose"
    else
        echo "❌ Neither 'docker compose' nor 'docker-compose' is available"
        exit 1
    fi
fi

echo "📦 Using: $DOCKER_COMPOSE_CMD"

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Please create one with required environment variables."
    echo "   Example variables needed:"
    echo "   OPENPROJECT_SECRET_KEY_BASE=your-secret-key-here"
    exit 1
fi

# Pull latest images
echo "📥 Pulling latest OpenProject image..."
$DOCKER_COMPOSE_CMD pull openproject

# Stop the service gracefully (if running)
echo "🛑 Stopping existing OpenProject service..."
$DOCKER_COMPOSE_CMD stop openproject 2>/dev/null || true

# Remove the old container (keeps volumes intact)
echo "🗑️  Removing old container (data will be preserved)..."
$DOCKER_COMPOSE_CMD rm -f openproject 2>/dev/null || true

# Start the service with new image
echo "▶️  Starting OpenProject with latest image..."
$DOCKER_COMPOSE_CMD up -d openproject

# Connect to bridge network for nginx-proxy discovery
echo "🔗 Connecting OpenProject to bridge network for proxy discovery..."
docker network connect bridge openproject 2>/dev/null || echo "Already connected to bridge network"

# Restart nginx-proxy to discover the new container
echo "🔄 Restarting nginx-proxy for container discovery..."
docker restart nginx-proxy 2>/dev/null || echo "nginx-proxy not found - skipping restart"

# Wait for healthcheck
echo "🏥 Waiting for OpenProject to be healthy..."
timeout=300  # 5 minutes
counter=0

while [ $counter -lt $timeout ]; do
    if $DOCKER_COMPOSE_CMD ps openproject | grep -q "healthy"; then
        echo "✅ OpenProject is healthy and ready!"
        echo "🌐 Access OpenProject at: http://openproject.home:9090"
        break
    elif $DOCKER_COMPOSE_CMD ps openproject | grep -q "unhealthy"; then
        echo "❌ OpenProject health check failed"
        echo "📋 Showing logs:"
        $DOCKER_COMPOSE_CMD logs --tail=50 openproject
        exit 1
    else
        echo "⏳ Waiting for OpenProject to start... ($counter/$timeout seconds)"
        sleep 10
        counter=$((counter + 10))
    fi
done

if [ $counter -ge $timeout ]; then
    echo "⏰ Timeout waiting for OpenProject to become healthy"
    echo "📋 Showing logs:"
    $DOCKER_COMPOSE_CMD logs --tail=50 openproject
    exit 1
fi

echo ""
echo "🎉 OpenProject deployment completed successfully!"
echo "📊 Container status:"
$DOCKER_COMPOSE_CMD ps openproject

echo ""
echo "💾 Volume information:"
docker volume ls | grep openproject || echo "No OpenProject volumes found (this might be normal for first run)"