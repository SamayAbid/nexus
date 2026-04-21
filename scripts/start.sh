#!/usr/bin/env bash
set -e
mkdir -p logs data
echo "Starting NEXUS agent and API..."
supervisord -c scripts/supervisord.conf &
echo "Starting ngrok tunnel..."
bash scripts/tunnel.sh &
echo "NEXUS is running. Press Ctrl+C to stop."
wait
