#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(cd "$SCRIPT_DIR/../backend" && pwd)"

TARGET_ENV="development"
EXTRA_ARGS=()

while [[ $# -gt 0 ]]; do
    case "$1" in
        -e|--env|--environment)
            TARGET_ENV="$2"
            shift 2
            ;;
        --env=*)
            TARGET_ENV="${1#*=}"
            shift
            ;;
        *)
            EXTRA_ARGS+=("$1")
            shift
            ;;
    esac
done

if [[ "$TARGET_ENV" =~ ^(prod|production)$ ]]; then
    export ENVIRONMENT="production"
    export ENV_FILE=".env.production"
    TARGET_BUCKET="smart-farming-data"
else
    export ENVIRONMENT="development"
    export ENV_FILE=".env"
    TARGET_BUCKET="smart-farming-data-dev"
fi

echo "========================================================"
echo " Starting Server 1: Main Backend API (Port 8000)"
echo " Environment   : ${ENVIRONMENT^^}"
echo " Config File   : $ENV_FILE"
echo " Storage Engine: Supabase Object Storage"
echo " Target Bucket : $TARGET_BUCKET"
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

exec $UVICORN_BIN app.main:app --app-dir src --host 127.0.0.1 --port 8000 --reload "${EXTRA_ARGS[@]}"
