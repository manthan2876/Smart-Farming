# Incident Management & Triage Runbook

**Project:** Smart Farming Platform  
**Standard:** Phase 5 Production-Readiness Specification  
**Classification:** Incident Response & Operational Continuity  
**Last Updated:** October 2026  

---

## 1. Severity Classifications

| Severity | Definition | Response Target | Escalation Target |
| :--- | :--- | :--- | :--- |
| **SEV-1 (Critical)** | Core platform outage: `/predict`, database, or authentication completely down for all users. | < 15 minutes | Lead Backend & DevOps Engineer |
| **SEV-2 (High)** | Degradation: AI vision microservice slow (> 10s), worker queue backpressure, or translation fallback triggering widely. | < 1 hour | Backend / ML Engineer |
| **SEV-3 (Medium)** | Non-blocking bug: UI cosmetic issue, specific obscure device camera distortion, localized text typo. | Next Business Day | Frontend / Mobile Engineer |

---

## 2. Fast Diagnosis Checklist

When alerted to an operational anomaly:

```bash
# 1. Check HTTP Health & Readiness
curl -s http://127.0.0.1:8000/api/v1/health
curl -s http://127.0.0.1:8000/api/v1/ready
curl -s http://127.0.0.1:8000/api/v1/queue-health

# 2. Inspect Prometheus Metrics
curl -s http://127.0.0.1:8000/api/v1/metrics | grep smart_farming

# 3. Check Real-Time Logs for Exceptions
docker compose logs -f --tail=100 backend worker
```

---

## 3. SEV-1 Outage Runbooks

### Runbook 1: Database Unavailability (`HTTP 503 Database is not ready`)
1. **Verify Database Process**:
   - `pg_isready -h localhost -p 5432 -U test_user` (PostgreSQL) or check disk space for SQLite (`df -h`).
2. **Examine Connection Saturation**:
   - Query active connections: `SELECT count(*), state FROM pg_stat_activity GROUP BY state;`.
   - If pool exhausted, restart backend or increase `pool_size` / `max_overflow` in `backend/src/app/core/session.py`.
3. **If Database Corrupted**:
   - Execute restore drill: see [`Docs/Backup_Restore_Runbook.md`](file:///home/manthan/Projects/Smart-Farming/Docs/Backup_Restore_Runbook.md).

### Runbook 2: Hugging Face AI Microservice Outage
1. **Symptom**: `504 Gateway Timeout` or `502 Bad Gateway` on image uploads.
2. **Diagnosis**:
   - Ping AI space health: `curl -s https://maharsh8805-smart-farming-ai.hf.space/health`.
3. **Mitigation**:
   - If Space has gone to sleep: Ping endpoint to wake it up (takes ~30s on free CPU spaces).
   - Verify external keepalive cron ping on `cron-jobs.org` is firing every 10 minutes.

---

## 4. Rollback Procedures

### Container Deployment Rollback
```bash
# 1. Rollback to previous stable image tag
docker compose stop backend worker frontend
docker tag smart-farming-backend:previous smart-farming-backend:latest
docker compose up -d

# 2. Verify health
curl --fail http://127.0.0.1:8080/ready
```

### Database Migration Rollback (Alembic)
```bash
cd backend
# Downgrade single revision
uv run alembic downgrade -1
```

