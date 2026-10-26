from __future__ import annotations

import os
import sqlite3
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def test_database_backup_and_restore_cycle(tmp_path: Path):
    """Verify Phase 5 database backup, SHA-256 integrity, retention, and restore drill."""
    # 1. Create a dummy SQLite database with test tables and records
    test_db = tmp_path / "test_farm.db"
    conn = sqlite3.connect(test_db)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE farmers (id INTEGER PRIMARY KEY, name TEXT, region TEXT);")
    cursor.execute("INSERT INTO farmers (name, region) VALUES ('Manthan', 'Anand, Gujarat');")
    cursor.execute("INSERT INTO farmers (name, region) VALUES ('Kunj', 'Rajkot, Gujarat');")
    conn.commit()
    conn.close()

    backup_dir = tmp_path / "backups"
    backup_script = REPO_ROOT / "scripts" / "backup_database.sh"
    restore_script = REPO_ROOT / "scripts" / "restore_database.sh"

    assert backup_script.exists()
    assert restore_script.exists()

    # 2. Run backup script
    env = os.environ.copy()
    env["BACKUP_DIR"] = str(backup_dir)
    env["DATABASE_URL"] = f"sqlite:///{test_db}"
    env["RETENTION_DAYS"] = "7"

    result = subprocess.run(
        ["bash", str(backup_script)],
        env=env,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"Backup failed: {result.stderr}"
    assert "[SUCCESS] Backup completed:" in result.stdout

    # Verify backup archive and sha256 manifest exist
    archives = list(backup_dir.glob("smart_farming_backup_*.sqlite.gz"))
    assert len(archives) == 1
    archive = archives[0]
    sha_file = archive.with_suffix(".gz.sha256")
    assert sha_file.exists()

    # 3. Run restore drill
    restore_result = subprocess.run(
        ["bash", str(restore_script), str(archive), "drill"],
        env=env,
        capture_output=True,
        text=True,
    )
    assert restore_result.returncode == 0, f"Restore drill failed: {restore_result.stderr}"
    assert "[SUCCESS] Cryptographic checksum verified:" in restore_result.stdout
    assert "Restore drill verified:" in restore_result.stdout

    # 4. Test tampering detection
    corrupted_archive = tmp_path / "corrupted.sqlite.gz"
    corrupted_archive.write_bytes(archive.read_bytes() + b"corrupt_noise")
    corrupted_sha = corrupted_archive.with_suffix(".gz.sha256")
    corrupted_sha.write_text(sha_file.read_text())  # original hash, mismatched content

    tamper_result = subprocess.run(
        ["bash", str(restore_script), str(corrupted_archive), "drill"],
        env=env,
        capture_output=True,
        text=True,
    )
    assert tamper_result.returncode == 2, "Expected checksum failure on tampered archive"
    assert "[CRITICAL] Checksum mismatch!" in tamper_result.stdout

