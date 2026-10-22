#!/usr/bin/env bash
# ==============================================================================
# Smart Farming Database Restore & Verification Script (Phase 5 Recovery Drill)
# ==============================================================================
set -euo pipefail

if [[ $# -lt 1 ]]; then
    echo "Usage: $0 <path-to-backup-archive.gz> [target-database-url]"
    exit 1
fi

BACKUP_FILE="$1"
TARGET_DATABASE_URL="${2:-${TARGET_DATABASE_URL:-drill}}"

if [[ ! -f "${BACKUP_FILE}" ]]; then
    echo "[ERROR] Backup file not found: ${BACKUP_FILE}"
    exit 1
fi

# Step 1: Validate SHA-256 Checksum
SHA_FILE="${BACKUP_FILE}.sha256"
if [[ -f "${SHA_FILE}" ]]; then
    echo "[INFO] Verifying SHA-256 checksum..."
    EXPECTED_SHA="$(cat "${SHA_FILE}" | awk '{print $1}')"
    ACTUAL_SHA="$(sha256sum "${BACKUP_FILE}" | awk '{print $1}')"
    if [[ "${EXPECTED_SHA}" != "${ACTUAL_SHA}" ]]; then
        echo "[CRITICAL] Checksum mismatch! Expected ${EXPECTED_SHA}, got ${ACTUAL_SHA}. Aborting restore."
        exit 2
    fi
    echo "[SUCCESS] Cryptographic checksum verified: ${ACTUAL_SHA}"
else
    echo "[WARNING] No .sha256 manifest found beside archive; proceeding with decompression test."
fi

# Step 2: Restore / Drill Execution
if [[ "${BACKUP_FILE}" =~ \.sqlite\.gz$ ]]; then
    DRILL_TARGET="${BACKUP_FILE%.gz}.restored_drill.db"
    echo "[INFO] Decompressing SQLite archive to ${DRILL_TARGET}..."
    gunzip -c "${BACKUP_FILE}" > "${DRILL_TARGET}"

    echo "[INFO] Running integrity check on restored database..."
    if command -v sqlite3 >/dev/null 2>&1; then
        INTEGRITY_RESULT="$(sqlite3 "${DRILL_TARGET}" "PRAGMA integrity_check;")"
        if [[ "${INTEGRITY_RESULT}" != "ok" ]]; then
            echo "[CRITICAL] Restored SQLite database failed integrity check: ${INTEGRITY_RESULT}"
            rm -f "${DRILL_TARGET}"
            exit 3
        fi
        TABLE_COUNT="$(sqlite3 "${DRILL_TARGET}" "SELECT count(*) FROM sqlite_master WHERE type='table';")"
        echo "[SUCCESS] Restore drill verified: ${TABLE_COUNT} tables found and integrity is OK."
    elif command -v python3 >/dev/null 2>&1; then
        python3 -c "
import sqlite3, sys
conn = sqlite3.connect('${DRILL_TARGET}')
res = conn.execute('PRAGMA integrity_check;').fetchone()[0]
if res != 'ok':
    print(f'[CRITICAL] SQLite integrity failed: {res}')
    sys.exit(3)
count = conn.execute(\"SELECT count(*) FROM sqlite_master WHERE type='table';\").fetchone()[0]
print(f'[SUCCESS] Restore drill verified: {count} tables found and integrity is OK.')
"
    fi

    if [[ "${TARGET_DATABASE_URL}" == "drill" ]]; then
        echo "[INFO] Drill complete. Removing temporary restore file."
        rm -f "${DRILL_TARGET}"
    elif [[ "${TARGET_DATABASE_URL}" =~ ^sqlite:///(.*)$ ]]; then
        DEST="${BASH_REMATCH[1]}"
        echo "[INFO] Deploying restored database to target: ${DEST}"
        mv -f "${DRILL_TARGET}" "${DEST}"
        echo "[SUCCESS] Database restoration complete!"
    fi
elif [[ "${BACKUP_FILE}" =~ \.pgdump\.gz$ ]]; then
    if [[ "${TARGET_DATABASE_URL}" == "drill" ]]; then
        echo "[INFO] Testing gzip decompression archive integrity for PostgreSQL dump..."
        gzip -t "${BACKUP_FILE}"
        echo "[SUCCESS] PostgreSQL dump archive is uncorrupted and readable."
    elif [[ "${TARGET_DATABASE_URL}" =~ ^postgresql:// ]]; then
        echo "[INFO] Restoring PostgreSQL dump to ${TARGET_DATABASE_URL}..."
        gunzip -c "${BACKUP_FILE}" | psql "${TARGET_DATABASE_URL}"
        echo "[SUCCESS] PostgreSQL restore completed successfully!"
    fi
fi

echo "[SUCCESS] Restore operation / drill verified without errors."
