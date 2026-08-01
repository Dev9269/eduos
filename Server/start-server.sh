#!/bin/bash
# EduOS Server Startup Script
# Run this on the admin laptop (gaming laptop / designated server)
# Usage: bash Server/start-server.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "╔══════════════════════════════════════╗"
echo "║     EduOS Admin Server v1.0          ║"
echo "╚══════════════════════════════════════╝"
echo ""

# Check Python
if ! command -v python3 &>/dev/null; then
    echo "ERROR: Python3 not found. Install it first."
    exit 1
fi

# Install dependencies if needed
echo "[1/3] Checking dependencies..."
pip3 install fastapi uvicorn websockets pyjwt psutil \
    --quiet --break-system-packages 2>/dev/null || \
pip3 install fastapi uvicorn websockets pyjwt psutil --quiet

# Show server IP so admin knows what to configure on agents
echo "[2/3] Detecting server IP..."
SERVER_IP=$(hostname -I | awk '{print $1}')
echo ""
echo "  Server IP: ${SERVER_IP}"
echo "  Port: 8765"
echo "  Agent config: set server_url to ws://${SERVER_IP}:8765"
echo ""

# Start server
echo "[3/3] Starting EduOS Server..."
echo "  Press Ctrl+C to stop"
echo ""

cd "$PROJECT_DIR"
export EDUOS_DB_PATH="${HOME}/.eduos/server.db"
mkdir -p "${HOME}/.eduos"

python3 Server/eduos_server.py
