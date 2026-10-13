#!/usr/bin/env bash
# ==============================================================================
# verify_storage.sh — Test & Verify Cloud Object Storage Connectivity
# Usage:
#   ./scripts/verify_storage.sh               # Verify Development Bucket (smartfarming-data-dev)
#   ./scripts/verify_storage.sh --env prod    # Verify Production Bucket (smart-farming-data)
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(cd "$SCRIPT_DIR/../backend" && pwd)"
MODEL_DIR="$(cd "$SCRIPT_DIR/../model_service" && pwd)"

# Resolve Python binary
if [ -n "${VIRTUAL_ENV:-}" ] && [ -x "$VIRTUAL_ENV/bin/python" ]; then
    PYTHON_BIN="$VIRTUAL_ENV/bin/python"
elif [ -x "$BACKEND_DIR/.venv/bin/python" ]; then
    PYTHON_BIN="$BACKEND_DIR/.venv/bin/python"
elif [ -x "$MODEL_DIR/.venv/bin/python" ]; then
    PYTHON_BIN="$MODEL_DIR/.venv/bin/python"
elif [ -x "$HOME/.venvs/smart-farming-backend/bin/python" ]; then
    PYTHON_BIN="$HOME/.venvs/smart-farming-backend/bin/python"
elif command -v python3 >/dev/null 2>&1; then
    PYTHON_BIN="python3"
else
    echo "Error: Python executable not found." >&2
    exit 1
fi

cd "$BACKEND_DIR"
export PYTHONPATH="$BACKEND_DIR/src:${PYTHONPATH:-}"

exec "$PYTHON_BIN" "$BACKEND_DIR/scripts/verify_supabase_storage.py" "$@"

