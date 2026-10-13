#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(cd "$SCRIPT_DIR/../backend" && pwd)"

echo "========================================================"
echo " Starting Server 1: Main Backend API (Port 8000)"
echo "========================================================"

cd "$BACKEND_DIR"

# Resolve uvicorn binary
if [ -n "${VIRTUAL_ENV:-}" ] && [ -x "$VIRTUAL_ENV/bin/uvicorn" ]; then
    UVICORN_BIN="$VIRTUAL_ENV/bin/uvicorn"
elif [ -x "$BACKEND_DIR/.venv/bin/uvicorn" ]; then
    UVICORN_BIN="$BACKEND_DIR/.venv/bin/uvicorn"
elif [ -x "$HOME/.venvs/smart-farming-backend/bin/uvicorn" ]; then
    UVICORN_BIN="$HOME/.venvs/smart-farming-backend/bin/uvicorn"
elif command -v uvicorn >/dev/null 2>&1; then
    UVICORN_BIN="uvicorn"
else
    UVICORN_BIN="python3 -m uvicorn"
fi
export PYTHONPATH="$BACKEND_DIR/src:${PYTHONPATH:-}"

exec $UVICORN_BIN app.main:app --app-dir src --host 127.0.0.1 --port 8000 --reload
