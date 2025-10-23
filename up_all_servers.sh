#!/bin/bash
# Script to start both the backend and frontend development servers for the project.

# Start backend (FastAPI+uvicorn) server
echo "Starting backend server ..."
cd backend
nohup uvicorn main:app --reload --port 8000 > ../backend_server.log 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > ../backend_server.pid
cd ..

# Start frontend (Vite+React) dev server
echo "Starting frontend (Vite) server ..."
cd frontend
nohup npm run dev > ../frontend_server.log 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID > ../frontend_server.pid
cd ..

echo "Backend PID: $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"
echo "Servers launched. Logs: backend_server.log, frontend_server.log"
