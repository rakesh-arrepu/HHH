#!/bin/bash

# Daily Tracker - Stop Script
# Stops any running backend and frontend servers

echo "Stopping Daily Tracker servers..."

# Kill uvicorn (backend)
pkill -f "uvicorn main:app" 2>/dev/null && echo "Backend stopped" || echo "Backend not running"

# Kill vite (frontend)
pkill -f "vite" 2>/dev/null && echo "Frontend stopped" || echo "Frontend not running"

echo "Done!"
