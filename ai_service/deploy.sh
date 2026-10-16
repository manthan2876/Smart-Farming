#!/usr/bin/env bash
set -e

# ==============================================================================
# deploy_hf_space.sh — Deploy ai_service changes directly to Hugging Face Space
#
# This script keeps your main monorepo 100% clean and isolated:
# - Maintains a lightweight Git LFS deployment mirror in .hf_space/
# - Preserves Git LFS pointers for model weights (avoiding the 10 MiB limit)
# - Synchronizes updated code, configs, routers, and prompts
# - Commits and pushes changes directly to the Hugging Face Space repository
# ==============================================================================

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
AI_DIR="$REPO_ROOT/ai_service"
DEPLOY_DIR="$REPO_ROOT/.hf_space"
HF_SPACE_URL="https://huggingface.co/spaces/Maharsh8805/smart-farming-ai"
COMMIT_MSG="${1:-deploy(ai_service): sync updates from main repository}"

# Prevent Git LFS from ever downloading 150+ MB model blobs locally
export GIT_LFS_SKIP_SMUDGE=1

echo "🌾 [Hugging Face Deployer] Initializing sync..."

# 1. Initialize or update .hf_space mirror
if [ ! -d "$DEPLOY_DIR/.git" ]; then
    echo "📦 Cloning lightweight Space deployment mirror into .hf_space..."
    rm -rf "$DEPLOY_DIR"
    GIT_LFS_SKIP_SMUDGE=1 git clone --depth 1 "$HF_SPACE_URL" "$DEPLOY_DIR"
else
    echo "🔄 Refreshing Space deployment mirror..."
    cd "$DEPLOY_DIR"
    git fetch origin main --depth=1 2>/dev/null || true
    git reset --hard origin/main 2>/dev/null || true
    cd "$REPO_ROOT"
fi

# 2. Synchronize configuration and entrypoint files
echo "📋 Synchronizing source files..."
for f in app.py main.py requirements.txt README.md config.yaml advisory_kb.json packages.txt Dockerfile; do
    if [ -f "$AI_DIR/$f" ]; then
        cp "$AI_DIR/$f" "$DEPLOY_DIR/$f"
    fi
done

# Synchronize python modules and engines
for dir in core routers vision_engine training; do
    if [ -d "$AI_DIR/$dir" ]; then
        rsync -rlt --delete \
            --exclude="__pycache__" \
            --exclude="*.pyc" \
            --exclude=".pytest_cache" \
            "$AI_DIR/$dir/" "$DEPLOY_DIR/$dir/" > /dev/null
    fi
done

# Synchronize model labels, manifests, matrices and configs (preserving LFS pointers for .pth/.pt)
mkdir -p "$DEPLOY_DIR/models"
find "$AI_DIR/models" -type f \( -name "*.json" -o -name "*.csv" -o -name "*.png" -o -name "*.yaml" \) | while read -r file; do
    rel_path="${file#$AI_DIR/models/}"
    dest_path="$DEPLOY_DIR/models/$rel_path"
    mkdir -p "$(dirname "$dest_path")"
    cp "$file" "$dest_path"
done

# 3. Check for any detected modifications
cd "$DEPLOY_DIR"
if [ -z "$(git status --porcelain)" ]; then
    echo "✅ Hugging Face Space is already up to date with ai_service/. Nothing to deploy."
    exit 0
fi

echo "📝 Changes detected:"
git status --short

echo "🚀 Committing and pushing to Hugging Face Space..."
git add .
git commit -m "$COMMIT_MSG"
git push origin main

echo ""
echo "🎉 Successfully deployed to Hugging Face Space!"
echo "🔗 Space URL: $HF_SPACE_URL"
echo "🌐 API Endpoint: https://maharsh8805-smart-farming-ai.hf.space"
