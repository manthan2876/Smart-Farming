#!/usr/bin/env bash
# ==============================================================================
# Smart Farming Database Backup & Retention Script (Phase 5 Recovery Operations)
# ==============================================================================
set -euo pipefail

BACKUP_DIR="${BACKUP_DIR:-./backups}"
RETENTION_DAYS="${RETENTION_DAYS:-14}"
TIMESTAMP="$(date -u +"%Y%m%d_%H%M%SZ")"
DATABASE_URL="${DATABASE_URL:-sqlite:///./dev_database.db}"

mkdir -p "${BACKUP_DIR}"

echo "[INFO] Starting database backup at ${TIMESTAMP}"
echo "[INFO] Target directory: ${BACKUP_DIR}"
echo "[INFO] Retention policy: ${RETENTION_DAYS} days"

if [[ "${DATABASE_URL}" =~ ^sqlite:///(.*)$ ]]; then
    DB_FILE="${BASH_REMATCH[1]}"
    if [[ ! -f "${DB_FILE}" ]]; then
        echo "[ERROR] SQLite database file not found at ${DB_FILE}"
        exit 1
    fi
    BACKUP_FILE="${BACKUP_DIR}/smart_farming_backup_${TIMESTAMP}.sqlite.gz"
    echo "[INFO] Backing up SQLite database ${DB_FILE}..."
    if command -v sqlite3 >/dev/null 2>&1; then
        sqlite3 "${DB_FILE}" ".backup '${BACKUP_DIR}/temp_${TIMESTAMP}.db'"
        gzip -c "${BACKUP_DIR}/temp_${TIMESTAMP}.db" > "${BACKUP_FILE}"
        rm -f "${BACKUP_DIR}/temp_${TIMESTAMP}.db"
    elif command -v python3 >/dev/null 2>&1; then
        python3 -c "
import sqlite3
src = sqlite3.connect('${DB_FILE}')
dst = sqlite3.connect('${BACKUP_DIR}/temp_${TIMESTAMP}.db')
src.backup(dst)
dst.close()
src.close()
"
        gzip -c "${BACKUP_DIR}/temp_${TIMESTAMP}.db" > "${BACKUP_FILE}"
        rm -f "${BACKUP_DIR}/temp_${TIMESTAMP}.db"
    else
        gzip -c "${DB_FILE}" > "${BACKUP_FILE}"
    fi
elif [[ "${DATABASE_URL}" =~ ^postgresql://([^:]+):([^@]+)@([^:/]+):?([0-9]*)/([^?]+) ]]; then
    BACKUP_FILE="${BACKUP_DIR}/smart_farming_backup_${TIMESTAMP}.pgdump.gz"
    echo "[INFO] Backing up PostgreSQL database..."
    if command -v pg_dump >/dev/null 2>&1; then
        pg_dump "${DATABASE_URL}" | gzip > "${BACKUP_FILE}"
    else
        echo "[ERROR] pg_dump utility not installed on system."
        exit 1
    fi
else
    echo "[ERROR] Unsupported or malformed DATABASE_URL: ${DATABASE_URL}"
    exit 1
fi

# Generate cryptographic SHA-256 integrity manifest
CHECKSUM="$(sha256sum "${BACKUP_FILE}" | awk '{print $1}')"
echo "${CHECKSUM}  $(basename "${BACKUP_FILE}")" > "${BACKUP_FILE}.sha256"

FILE_SIZE="$(du -h "${BACKUP_FILE}" | cut -f1)"
echo "[SUCCESS] Backup completed: ${BACKUP_FILE} (${FILE_SIZE})"
echo "[SUCCESS] Integrity SHA-256: ${CHECKSUM}"

# Enforce retention policy
echo "[INFO] Enforcing retention: purging backups older than ${RETENTION_DAYS} days..."
find "${BACKUP_DIR}" -type f \( -name "smart_farming_backup_*.gz" -o -name "smart_farming_backup_*.sha256" \) -mtime +"${RETENTION_DAYS}" -exec rm -f {} +
echo "[INFO] Retention cleanup finished."
