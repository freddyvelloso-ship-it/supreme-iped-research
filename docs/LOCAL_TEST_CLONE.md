# SUPREME V4 - Local Test Clone

This clone was extracted from the final Phase 7 release ZIP for local testing.
It includes generated local env files and local TLS certificates that must not be
shipped as a release.

Use this compose stack to avoid port conflicts with the main working copy:

```powershell
docker compose -f docker-compose.production.yml -f docker-compose.local.yml -f docker-compose.test-clone.yml up -d --build
```

Test clone URLs:

- NGINX HTTPS: `https://localhost:8448`
- SUPREME API: `http://localhost:18000`
- SENTINELA: `http://localhost:18001`
- Grafana: `http://localhost:3300`
- Prometheus: `http://localhost:9190`
- Mailpit: `http://localhost:8026`

Run local E2E:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\local.ps1 -Action test -PythonExe "C:\Users\nunas\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" -TimeoutSeconds 180
```
