# Field Chain Of Custody

Phase 8 extends custody from IPED UI observation to central analytics.

## Chain

1. IPED plugin observes result selection.
2. Plugin emits privacy-minimized event.
3. Plugin event includes event hash and local chain hash.
4. Agent wraps event into a signed envelope.
5. Agent stores encrypted queue row.
6. Agent sends mapped SUPREME ingest event to the central API.
7. SUPREME persists raw event and runs deterministic analytics.
8. SENTINELA visualizes backend outputs only.
9. Replay checks plugin event -> envelope -> SUPREME event -> output hash.

## Evidence Files

- `supreme-iped-plugin/dist/supreme-iped-plugin-manifest.json`
- `reports/phase8/field_replay_report.json`
- agent queue records in deployment-specific protected storage
- central SUPREME/SENTINELA audit records

## Replay

```powershell
python scripts\phase8_field_forensic_replay.py --root .
```

The replay fails if signatures, chain order or deterministic output mapping
diverge.

## Current Boundary

The replay currently proves plugin event -> agent envelope -> central ingest
mapping for supported event types. Production field certification still requires
real signed binaries, external SUPREME/SENTINELA, server-issued device
credentials and a live central ingestion audit trail.
