# SUPREME V4 - SLO and Observability

## SLOs

- SUPREME API availability: 99.5% monthly.
- SENTINELA availability: 99.5% monthly.
- Ingest latency p95: less than 2 seconds.
- Event-to-analytic-window latency p95: less than 5 minutes.
- DLQ objective: zero untriaged jobs.
- Backup objective: daily backup and monthly restore test.

## Burn Rate

Burn rate alerts exist in `infra/prometheus/alert_rules.yml`:

- `SLOBurnRateAPI`
- `SLOBurnRatePipeline`

## Dashboards and Alerts

Prometheus, Grafana, Loki and Alertmanager are part of the production stack.
Alerts must link to runbooks under `docs/runbooks`.

## Evidence

Run:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\phase7_observability_slo_check.ps1 -Root .
```

