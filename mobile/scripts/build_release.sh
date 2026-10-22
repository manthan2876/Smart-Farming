#!/usr/bin/env bash
# ==============================================================================
# Smart Farming Mobile Release Build Script (Phase 6 Production Readiness)
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MOBILE_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${MOBILE_DIR}"

echo "[INFO] Starting Smart Farming Mobile Release Build..."

# 1. Dependency check
if ! command -v flutter >/dev/null 2>&1; then
    echo "[ERROR] Flutter SDK not found in PATH."
    exit 1
fi

# 2. Dependency sync
echo "[INFO] Fetching locked Flutter dependencies..."
flutter pub get --enforce-lockfile

# 3. Static analysis & test gate
echo "[INFO] Running Flutter static analysis and tests..."
flutter analyze --no-fatal-infos
flutter test

# 4. Signing check
if [ ! -f "android/key.properties" ] && [ -z "${ANDROID_KEYSTORE_PATH:-}" ]; then
    echo "[WARNING] No signing configuration (android/key.properties or ANDROID_KEYSTORE_PATH) found."
    echo "[WARNING] The build will be unsigned."
fi

# 5. Build release App Bundle with code obfuscation and split debug symbols
echo "[INFO] Building Android App Bundle with Dart code obfuscation..."
mkdir -p build/app/outputs/symbols

flutter build appbundle --release \
    --obfuscate \
    --split-debug-info=build/app/outputs/symbols

echo "[SUCCESS] Build finished successfully!"
echo "[SUCCESS] Artifact: ${MOBILE_DIR}/build/app/outputs/bundle/release/app-release.aab"
echo "[SUCCESS] Symbols:  ${MOBILE_DIR}/build/app/outputs/symbols"

