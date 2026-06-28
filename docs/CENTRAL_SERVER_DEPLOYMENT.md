# SUPREME Central Server Deployment

The central deployment owns all durable analytical state.

## Components

- SUPREME API.
- SUPREME worker/RQ.
- Redis.
- Postgres.
- SENTINELA.
- NGINX/TLS.
- Prometheus/Grafana/Alertmanager.
- Backup and restore automation.

## Field Machine Boundary

Perito workstations run only:

- official IPED;
- signed SUPREME IPED plugin;
- local SUPREME Windows agent;
- encrypted local queue.

They must not run production Postgres, Redis, SENTINELA or analytics workers.

## External SENTINELA

`SENTINELA_URL` in production must be a real HTTPS URL, not localhost, an IP
loopback or an example domain. The existing readiness checks already reject
unsafe local/example values for production mode.

## Production Blockers

The current repository cannot produce a real production deployment until the
operator supplies:

- real DNS/domain;
- TLS certificate;
- SMTP/Alertmanager receiver;
- production secrets;
- device-pairing policy;
- code-signing certificate.
