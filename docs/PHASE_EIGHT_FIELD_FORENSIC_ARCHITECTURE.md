# SUPREME V4 - Phase 8 Field Forensic Architecture

Status: implementation path created; production completion is blocked until real
code-signing and external deployment credentials are supplied.

## Target Architecture

```text
Official IPED
  -> signed SUPREME ResultSetViewer plugin
  -> local SUPREME Windows agent
  -> encrypted local queue and hash chain
  -> central SUPREME API
  -> central Postgres/Redis/RQ
  -> external SENTINELA dashboard
```

## What Changed In Phase 8

- `supreme-iped-plugin` implements `iped.viewers.api.ResultSetViewer`.
- The plugin is loaded through IPED's `plugins` classpath plus
  `conf/ResultSetViewersConf.xml`, not through source-level UI patching.
- `supreme-agent-windows` reads plugin NDJSON events, creates signed envelopes,
  stores encrypted local queue rows and maps events to SUPREME ingest records.
- `scripts/install_supreme_iped_plugin.ps1` installs the plugin with XML backup,
  verification and rollback support.
- `scripts/phase8_field_forensic_architecture_check.ps1` checks the Phase 8
  acceptance surface and reports production blockers separately from code
  failures.

## IPED Extension Evidence

The official IPED codebase exposes:

- `PluginConfig.getPluginJars()`, adding `plugins` JARs to runtime classpath.
- `Bootstrap`, which adds `pluginFolder/*` to the child process classpath.
- `ResultSetViewersConf.xml`, which lists viewer classes.
- `XMLResultSetViewerConfiguration`, which uses `Class.forName(...)` to load
  configured viewers.
- `ResultSetViewer`, whose `init(...)` receives the results `JTable` and result
  provider.

This is sufficient for a plugin to observe result selection without a fork of
IPED. It is not sufficient to intercept every possible GUI action unless IPED
exposes that action through table selection, model updates or a future upstream
event bus.

## Production Acceptance Boundary

Phase 8 cannot be honestly declared 100% production complete without:

- a real organization-controlled code-signing certificate/keystore;
- a real external SENTINELA domain with TLS;
- a real central SUPREME/SENTINELA environment;
- device pairing credentials issued by that environment.

Until those are supplied, Phase 8 can pass local implementation gates but must
remain blocked for production field rollout.
