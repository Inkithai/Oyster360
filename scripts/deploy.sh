#!/bin/bash

# Oyster360 Production Deployment Script
set -e

echo "🚀 Starting Oyster360 Production Deployment"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if .env.production exists
if [ ! -f ".env.production" ]; then
    echo -e "${RED}Error: .env.production file not found${NC}"
    echo "Please copy .env.production.example to .env.production and update the values"
    exit 1
fi

# Load environment variables
export $(cat .env.production | grep -v '^#' | xargs)

echo -e "${YELLOW}Step 1: Running database migrations${NC}"
cd backend
alembic upgrade head
echo -e "${GREEN}✓ Database migrations completed${NC}"

echo -e "${YELLOW}Step 2: Building frontend${NC}"
cd ../frontend
npm run build
echo -e "${GREEN}✓ Frontend build completed${NC}"

echo -e "${YELLOW}Step 3: Building Docker images${NC}"
cd ..
docker compose -f docker-compose.prod.yml build
echo -e "${GREEN}✓ Docker images built${NC}"

echo -e "${YELLOW}Step 4: Starting services${NC}"
docker compose -f docker-compose.prod.yml up -d
echo -e "${GREEN}✓ Services started${NC}"

echo -e "${YELLOW}Step 5: Running health checks${NC}"
sleep 10

# Check backend health
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Backend is healthy${NC}"
else
    echo -e "${RED}✗ Backend health check failed${NC}"
    exit 1
fi

# Check frontend health
if curl -f http://localhost:3000 > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Frontend is healthy${NC}"
else
    echo -e "${RED}✗ Frontend health check failed${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Deployment completed successfully!${NC}"
echo ""
echo "Access your application at:"
echo "  Frontend: http://localhost:3000"
echo "  Backend:  http://localhost:8000/docs"
echo ""
echo "Don't forget to:"
echo "  1. Configure your domain DNS"
echo "  2. Set up SSL certificates"
echo "  3. Configure monitoring and alerts"
echo "  4. Set up backup procedures"