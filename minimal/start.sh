#!/bin/bash

# Daily Tracker - Start Script
# Starts both backend and frontend servers, then opens the browser

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Starting Daily Tracker...${NC}"

# Function to cleanup on exit
cleanup() {
    echo -e "\n${BLUE}Shutting down servers...${NC}"
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
    fi
    exit 0
}

trap cleanup SIGINT SIGTERM

# Check if backend venv exists, create if not
if [ ! -d "backend/venv" ]; then
    echo -e "${BLUE}Creating backend virtual environment...${NC}"
    cd backend
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    cd ..
else
    echo -e "${GREEN}Backend venv found${NC}"
fi

# Check if frontend node_modules exists, install if not
if [ ! -d "frontend/node_modules" ]; then
    echo -e "${BLUE}Installing frontend dependencies...${NC}"
    cd frontend
    npm install
    cd ..
else
    echo -e "${GREEN}Frontend node_modules found${NC}"
fi

# Start backend server
echo -e "${BLUE}Starting backend server on port 8000...${NC}"
cd backend
source venv/bin/activate
uvicorn main:app --reload --port 8000 &
BACKEND_PID=$!
cd ..

# Wait for backend to be ready
echo -e "${BLUE}Waiting for backend to start...${NC}"
for i in {1..30}; do
    if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
        echo -e "${GREEN}Backend is ready!${NC}"
        break
    fi
    sleep 1
done

# Start frontend server
echo -e "${BLUE}Starting frontend server on port 5173...${NC}"
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

# Wait for frontend to be ready and detect port
echo -e "${BLUE}Waiting for frontend to start...${NC}"
sleep 4

# Detect frontend port (vite may use 5174+ if 5173 is busy)
FRONTEND_PORT=5173
for port in 5173 5174 5175 5176; do
    if curl -s -o /dev/null -w "" http://localhost:$port 2>/dev/null; then
        FRONTEND_PORT=$port
        break
    fi
done

# Open browser
echo -e "${GREEN}Opening browser...${NC}"
if [[ "$OSTYPE" == "darwin"* ]]; then
    open http://localhost:$FRONTEND_PORT
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    xdg-open http://localhost:$FRONTEND_PORT 2>/dev/null || sensible-browser http://localhost:$FRONTEND_PORT
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    start http://localhost:$FRONTEND_PORT
fi

echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}Daily Tracker is running!${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "Frontend: ${BLUE}http://localhost:$FRONTEND_PORT${NC}"
echo -e "Backend:  ${BLUE}http://localhost:8000${NC}"
echo -e "API Docs: ${BLUE}http://localhost:8000/docs${NC}"
echo -e "\nPress ${BLUE}Ctrl+C${NC} to stop all servers"
echo -e "${GREEN}========================================${NC}\n"

# Wait for both processes
wait
