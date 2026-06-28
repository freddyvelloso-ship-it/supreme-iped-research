# SUPREME Windows Agent Operations

The Phase 8 local agent is in `supreme-agent-windows`.

## Responsibilities

- Read NDJSON events emitted by the IPED plugin.
- Create signed local envelopes.
- Maintain a hash chain.
- Store encrypted queue records with Fernet encryption.
- Retry delivery to the central SUPREME API.
- Build the current SUPREME `/v1/events/ingest` payload for supported field
  events.
- Verify scoped device credentials issued by the central pairing authority.
- Keep psychometric journey order deterministic:
  `SRQ20/DASS21/OLBI -> IPED -> PANAS_SHORT`.

## Required Environment

```powershell
$env:SUPREME_AGENT_ID="device-id-issued-by-server"
$env:SUPREME_INSTITUTION_ID="institution-id"
$env:SUPREME_STUDY_ID="study-id"
$env:SUPREME_CASE_ID="case-id"
$env:SUPREME_PARTICIPANT_SCOPE="operator-or-participant-scope"
$env:SUPREME_SERVER_URL="https://supreme.example.org"
$env:SUPREME_AGENT_INGEST_TOKEN="<short-lived-device-token>"
$env:SUPREME_AGENT_SIGNING_KEY="<device-secret-min-32-chars>"
$env:SUPREME_AGENT_ENCRYPTION_KEY="<device-secret-min-32-chars>"
$env:SUPREME_PLUGIN_EVENT_LOG="$env:USERPROFILE\supreme-field-events.ndjson"
```

Secrets must be provisioned by device pairing. They must not be written to docs,
PowerShell history, screenshots or repository files.

## Central Ingest Mapping

The current central SUPREME ingest endpoint accepts `file_open`, `image_view`,
`video_play` and `classification_event`. Field lifecycle events such as
`session_start`, `session_end` and `item_close` are preserved in the encrypted
local custody queue and replay report, but require a native central
field-session endpoint before they can be ingested without lossy mapping.

## Run Once

```powershell
python -m supreme_agent.agent
```

## Windows Service Readiness

The code is service-ready, but the actual Windows Service wrapper and code
signing are deployment artifacts. Recommended wrappers:

- NSSM for controlled field pilots;
- native Windows Service executable for production.

Production service installation must enforce:

- least-privilege local account;
- restricted queue directory ACL;
- outbound-only network access to SUPREME;
- log rotation and sanitization;
- certificate pinning or mTLS when available.
