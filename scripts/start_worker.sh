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
echo " Starting ARQ Background Worker (Redis Job Queue)"
echo " Environment   : ${ENVIRONMENT^^}"
echo " Config File   : $ENV_FILE"
echo " Storage Engine: Supabase Object Storage"
echo " Target Bucket : $TARGET_BUCKET"
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

exec $ARQ_BIN app.worker.WorkerSettings "${EXTRA_ARGS[@]}"
