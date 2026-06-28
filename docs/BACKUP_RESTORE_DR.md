# SUPREME V4 - Backup, Restore and Disaster Recovery

Backups are Postgres custom-format dumps for SUPREME and SENTINELA. Phase 7
restore testing must restore into temporary databases and drop them after
verification.

## Non-Destructive Gate

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\phase7_backup_restore_check.ps1
```

The gate creates dumps, restores them into temporary databases, checks that
public tables exist and writes a manifest under `backups/phase7`.

## Emergency Restore

Use `scripts/restore_postgres.ps1 -ConfirmRestore` only after approval from the
incident commander because it is destructive for the selected target database.

