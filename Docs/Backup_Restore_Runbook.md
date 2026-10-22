# Database Backup & Disaster Recovery Runbook

**Project:** Smart Farming Platform  
**Standard:** Phase 5 Production-Readiness Specification  
**Classification:** Operational Security & Reliability  
**Last Updated:** October 2026  

---

## 1. Objectives & Service Level Indicators (SLIs)

- **Recovery Point Objective (RPO)**: **< 1 Hour**  
  Maximum permissible data loss window in the event of hardware or cluster catastrophe.
- **Recovery Time Objective (RTO)**: **< 30 Minutes**  
  Maximum duration required to restore a valid backup and resume read/write database operations.

---

## 2. Automated Backup Strategy

The backup workflow is automated via [`scripts/backup_database.sh`](file:///home/manthan/Projects/Smart-Farming/scripts/backup_database.sh).

### Key Features
1. **Multi-Engine Support**:
   - **PostgreSQL**: Invokes `pg_dump` with stream gzip compression.
   - **SQLite**: Performs online zero-locking backup using SQLite online backup API (`src.backup(dst)`).
2. **Cryptographic Verification**:
   - Generates a standalone SHA-256 integrity manifest (`.sqlite.gz.sha256` or `.pgdump.gz.sha256`) immediately after creation.
3. **Automated Retention Enforcement**:
   - Automatically prunes backup archives and manifests older than `RETENTION_DAYS` (default 14 days).

### Scheduled Execution (Crontab)
To run automated hourly backups on Linux:
```bash
0 * * * * BACKUP_DIR=/var/backups/smart-farming RETENTION_DAYS=14 /opt/smart-farming/scripts/backup_database.sh >> /var/log/smart-farming-backup.log 2>&1
```

---

## 3. Restore & Disaster Recovery Drill

Restoration is managed via [`scripts/restore_database.sh`](file:///home/manthan/Projects/Smart-Farming/scripts/restore_database.sh).

### Step-by-Step Restoration Procedure

```bash
# 1. Locate the latest verified backup archive
LATEST_BACKUP=$(ls -t /var/backups/smart-farming/smart_farming_backup_*.gz | head -1)

# 2. Run non-destructive integrity drill test
bash scripts/restore_database.sh "$LATEST_BACKUP" drill

# 3. Perform actual restoration to target database
# For SQLite:
bash scripts/restore_database.sh "$LATEST_BACKUP" "sqlite:////app/data/smart-farming.db"

# For PostgreSQL:
bash scripts/restore_database.sh "$LATEST_BACKUP" "postgresql://user:pass@localhost:5432/smart_farming"
```

### Automated Verification in CI
The restoration drill is continuously tested in CI via [`backend/tests/test_backup_restore.py`](file:///home/manthan/Projects/Smart-Farming/backend/tests/test_backup_restore.py). Any regression in archive structure, checksum verification, or decompression halts release pipelines.

---

## 4. Offsite & Cloud Storage Synchronization

In production cloud environments (AWS / Supabase / GCP):
1. **Encrypted Bucket Replication**: Backup archives are synced to an offsite S3-compatible cold storage bucket (`aws s3 sync /var/backups s3://smart-farming-offsite-backups/`).
2. **Access Control**: Bucket access is governed by IAM policies enforcing AWS KMS server-side encryption with strict read-only access for restore workers.

