#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(cd "$SCRIPT_DIR/../backend" && pwd)"

echo "========================================================"
echo " Starting ARQ Background Worker (Redis Job Queue)"
echo "========================================================"

cd "$BACKEND_DIR"
export PYTHONIOENCODING="utf-8"

# Resolve arq binary
if [ -n "${VIRTUAL_ENV:-}" ] && [ -x "$VIRTUAL_ENV/bin/arq" ]; then
    ARQ_BIN="$VIRTUAL_ENV/bin/arq"
elif [ -x "$BACKEND_DIR/.venv/bin/arq" ]; then
    ARQ_BIN="$BACKEND_DIR/.venv/bin/arq"
elif [ -x "$HOME/.venvs/smart-farming-backend/bin/arq" ]; then
    ARQ_BIN="$HOME/.venvs/smart-farming-backend/bin/arq"
elif command -v arq >/dev/null 2>&1; then
    ARQ_BIN="arq"
else
    ARQ_BIN="python3 -m arq"
fi
export PYTHONPATH="$BACKEND_DIR/src:${PYTHONPATH:-}"

exec $ARQ_BIN app.worker.WorkerSettings
