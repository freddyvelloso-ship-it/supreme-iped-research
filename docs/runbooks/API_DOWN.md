# Runbook - SUPREME API Down

Check container health, recent logs, database connectivity and Redis. If the API
is unhealthy after dependency recovery, restart only `supreme-api` and record the
incident timeline.

