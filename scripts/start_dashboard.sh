#!/bin/bash
# Start the trading dashboard: FastAPI backend + Next.js frontend
# Usage: bash scripts/start_dashboard.sh
# Access: http://localhost:3000  (also http://<your-mac-ip>:3000 on mobile)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(dirname "$SCRIPT_DIR")"

echo "Starting trading dashboard..."
echo ""

# Kill any existing instances
pkill -f "uvicorn api.main" 2>/dev/null
pkill -f "next dev" 2>/dev/null
sleep 1

# Start FastAPI backend
uvicorn api.main:app --host 0.0.0.0 --port 8000 --app-dir "$ROOT" &
API_PID=$!
echo "  API backend: http://localhost:8000  (pid $API_PID)"

# Start Next.js dev server
cd "$ROOT/dashboard"
npm run dev &
UI_PID=$!
echo "  Dashboard:   http://localhost:3000  (pid $UI_PID)"

# Show your network IP for mobile access
IP=$(ipconfig getifaddr en0 2>/dev/null || hostname -I 2>/dev/null | awk '{print $1}')
if [ -n "$IP" ]; then
  echo ""
  echo "  Mobile URL:  http://${IP}:3000"
  echo "  (dashboard/.env.local already configured for mobile API access)"
fi

echo ""
echo "Press Ctrl+C to stop both servers."

trap "kill $API_PID $UI_PID 2>/dev/null; echo 'Stopped.'" EXIT INT TERM
wait
