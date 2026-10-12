#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MOBILE_DIR="$(cd "$SCRIPT_DIR/../mobile" && pwd)"

echo "========================================================"
echo " Starting Mobile App (Flutter - Chrome Device)"
echo "========================================================"

cd "$MOBILE_DIR"

if ! command -v flutter >/dev/null 2>&1; then
    echo "Warning: flutter command not found in PATH."
    echo "Please ensure Flutter SDK is installed and added to your PATH."
fi

exec flutter run -d chrome "$@"

