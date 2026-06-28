# External SENTINELA Access

SENTINELA must be reachable by authorized supervisors outside the perito local
machine.

## Production Requirements

- HTTPS domain controlled by the institution or operator.
- RBAC roles already defined: `master`, `pesquisador`, `auditor`, `operador`,
  `leitura_agregada`.
- Scope by institution, study, case and participant.
- HttpOnly cookie sessions.
- No token in browser storage.
- Audit logs for administrative changes.
- Backups and restore tests.

## Example Topology

```text
perito workstation
  -> outbound HTTPS
  -> https://supreme.example.org/v1/events/ingest

supervisor browser
  -> https://sentinela.example.org
```

`localhost` is acceptable only for local testing and must fail production
readiness.
