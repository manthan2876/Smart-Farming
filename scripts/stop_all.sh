#!/usr/bin/env bash
# ========================================================
# Stopping All Smart Farming Services...
# ========================================================

echo "========================================================"
echo " Stopping All Smart Farming Services..."
echo "========================================================"

echo "Stopping Uvicorn / ARQ / Python workers..."
pkill -f "uvicorn.*(src\.app\.main:app|main:app|8000|8001)" 2>/dev/null || true
pkill -f "arq.*WorkerSettings" 2>/dev/null || true

echo "Stopping Vite / Frontend dev servers..."
pkill -f "vite" 2>/dev/null || true

echo "Stopping Flutter / Dart processes..."
pkill -f "flutter.*run" 2>/dev/null || true

echo "Releasing ports 8000, 8001, 5173 if still bound..."
if command -v fuser >/dev/null 2>&1; then
    fuser -k 8000/tcp 2>/dev/null || true
    fuser -k 8001/tcp 2>/dev/null || true
    fuser -k 5173/tcp 2>/dev/null || true
fi

echo ""
echo "========================================================"
echo " All services stopped cleanly."
echo "========================================================"

