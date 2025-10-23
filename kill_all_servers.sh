#!/bin/bash
# Script to kill both backend and frontend dev servers previously started via up_all_servers.sh

kill_by_pidfile() {
    local pidfile="$1"
    local label="$2"
    if [ -f "$pidfile" ]; then
        PID=$(cat "$pidfile")
        if kill -0 "$PID" 2>/dev/null; then
            echo "Killing $label (PID: $PID)..."
            kill "$PID"
            rm -f "$pidfile"
        else
            echo "$label PID file found, but process $PID not running."
            rm -f "$pidfile"
        fi
    else
        echo "No $label PID file found."
    fi
}

kill_by_pattern() {
    local pattern="$1"
    local label="$2"
    # Find processes matching pattern, kill except the grep/this script itself
    for PID in $(ps aux | grep "$pattern" | grep -v grep | awk '{print $2}'); do
        echo "Killing $label process (PID: $PID)..."
        kill "$PID"
    done
}

echo "Attempting to kill backend and frontend dev servers ..."

kill_by_pidfile "backend_server.pid" "Backend server"
kill_by_pidfile "frontend_server.pid" "Frontend server"

# Fallback: kill by pattern if any remain
if pgrep -f "uvicorn main:app" > /dev/null ; then
    echo "Cleaning up any remaining uvicorn dev servers ..."
    kill_by_pattern "uvicorn main:app" "uvicorn"
fi

if pgrep -f "npm run dev" > /dev/null ; then
    echo "Cleaning up any remaining npm dev servers ..."
    kill_by_pattern "npm run dev" "npm run dev"
fi

echo "Kill all servers operation complete."
