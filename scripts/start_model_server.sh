#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODEL_DIR="$(cd "$SCRIPT_DIR/../model_service" && pwd)"
BACKEND_DIR="$(cd "$SCRIPT_DIR/../backend" && pwd)"

echo "========================================================"
echo " Starting Server 2: Model Inference Server (Port 8001)"
echo "========================================================"

cd "$MODEL_DIR"

# Resolve uvicorn binary
if [ -x "$MODEL_DIR/.venv/bin/uvicorn" ]; then
    UVICORN_BIN="$MODEL_DIR/.venv/bin/uvicorn"
elif [ -n "${VIRTUAL_ENV:-}" ] && [ -x "$VIRTUAL_ENV/bin/uvicorn" ]; then
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

exec $UVICORN_BIN main:app --host 127.0.0.1 --port 8001 --reload
