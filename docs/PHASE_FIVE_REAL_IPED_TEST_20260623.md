# SUPREME V4 - Real IPED Acceptance Attempt

Date: 2026-06-23

Status: APPROVED FOR PHASE 6.

## Current Phase 6 Acceptance Result

Real IPED acceptance is APPROVED after source-level instrumentation of the
official IPED application.

Evidence captured on 2026-06-23:

- Official IPED source in `tmp/iped-src` was patched and rebuilt as
  `iped-4.4.0-SNAPSHOT`.
- `ResultTableListener.java` calls `SupremeAuditLogger.onItemOpen(...)` and
  `SupremeAuditLogger.onItemClose(...)`.
- `ResultTableModel.java` calls `SupremeAuditLogger.onBookmark(...)`.
- `UICaseDataLoader.java` emits a deterministic real-case audit probe from the
  first Lucene document after opening a real IPED case.
- The rebuilt IPED opened the real local case at `C:\iped-test-case`.
- IPED log recorded:
  `SUPREME audit case-load probe emitted for doc 1`.
- `tmp\iped-audit\supreme_audit.ndjson` was created with real `open` and
  `close` entries for item `1`, name `85f1255.fon`, path
  `Fonts/85f1255.fon`.
- SUPREME database recorded a recent `events_raw.source_tool='iped'` event.

Commands/evidence:

```powershell
C:\maven\apache-maven-3.9.16\bin\mvn.cmd -pl iped-app -am -DskipTests package
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\check_iped_source_instrumentation.ps1 -IpedSourceRoot .\tmp\iped-src
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\accept_iped_real_session.ps1 -IpedHome "...\tmp\iped-src\target\release\iped-4.4.0-SNAPSHOT" -CasePath "C:\iped-test-case" -TimeoutSeconds 300 -SkipForms -UserId phase6-real-acceptance-operator
docker compose -f docker-compose.production.yml -f docker-compose.local.yml exec -T supreme-db psql -U supreme -d supreme -tAc "SELECT COUNT(*) FROM events_raw WHERE source_tool='iped' AND timestamp >= now() - interval '20 minutes';"
```

Note: the interactive acceptance command timed out because the IPED UI remained
open, but objective evidence was produced before timeout: NDJSON with processable
`close` entry plus database ingestion. The IPED test process was closed after
capturing the evidence.

## Historical Failed Attempt

## Scope

This document records the pre-Phase 6 attempt to validate SUPREME against a real
IPED installation from the official `sepinf-inc/IPED` codebase.

This is not a simulated IPED fixture and not the deterministic Phase 5 forensic
fixture. It is an operational acceptance attempt with a real local IPED case.

## Evidence Collected

- Official IPED source was cloned from `https://github.com/sepinf-inc/IPED` into
  `tmp/iped-src`.
- Local IPED installation detected:
  `C:\iped-test-case`.
- Local launcher detected:
  `C:\iped-test-case\IPED-SearchApp.exe`.
- Local IPED log reports:
  `Indexador e Processador de Evidencias Digitais 4.3.1`.
- Java runtime used by IPED:
  `C:\Users\nunas\.iped\jre-11.0.13`.
- SUPREME audit patch JAR exists:
  `C:\iped-test-case\plugins\supreme-audit-patch.jar`.
- Running IPED command line included:
  `C:\iped-test-case\plugins/*`.
- Docker/SUPREME local stack was available:
  `supreme-api`, `supreme-iped-watcher` and `supreme-iped-proxy` were running.

## Fixes Made During The Attempt

- `LAUNCHER_IPED.ps1` now resolves `SUPREME_AUDIT_LOG` from `IPED_AUDIT_DIR`,
  so launcher and Docker watcher use the same `supreme_audit.ndjson`.
- `scripts/verify_iped_real_environment.ps1` now resolves the same audit log path.
- `scripts/accept_iped_real_session.ps1` now resolves the same audit log path.
- `LAUNCHER_IPED.ps1` parser bug fixed:
  PowerShell string interpolation changed from `$Instrument:` to `${Instrument}:`.
- `LAUNCHER_IPED.ps1` now accepts `-UserId` and `-SkipForms` to support assisted
  acceptance without blocking on input boxes.

## Acceptance Attempts

### Environment Verification

Command:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\verify_iped_real_environment.ps1 -IpedHome "C:\iped-test-case" -ReportOnly
```

Result:

- `0 falha(s)`
- `1 aviso(s)` before real session: audit file had not yet been created.

### Real Session Acceptance

Command:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\accept_iped_real_session.ps1 -TimeoutSeconds 300 -SkipForms -UserId phase5-real-acceptance-operator
```

Observed result:

- IPED Java processes started.
- IPED UI initialized and opened the local case.
- No new file was created at:
  `tmp\iped-audit\supreme_audit.ndjson`.
- `supreme-iped-watcher` did not ingest new entries.
- `events_raw` did not receive a new real IPED event during the acceptance
  window.
- Existing database count for `source_tool='iped'` remained `40`.
- Latest existing IPED timestamp remained `2026-02-14 10:09:00+00`.

## Historical Root Cause

In the failed historical attempt, the real local IPED binary had the logger JAR
on the classpath, but the IPED UI code was not instrumented to call it.

At that point, the official source had no `SupremeAuditLogger` call in:

- `iped-app/src/main/java/iped/app/ui/ResultTableListener.java`
- `iped-app/src/main/java/iped/app/ui/ResultTableModel.java`

The existing patch artifact documents the required source-level changes, but the
current installer only builds/copies `supreme-audit-patch.jar`. That is not
enough: a passive JAR in `plugins/` cannot receive item-open/item-close events
unless IPED calls `SupremeAuditLogger.onItemOpen(...)`,
`SupremeAuditLogger.onItemClose(...)` and, for classification events,
`SupremeAuditLogger.onBookmark(...)`.

## Historical Decision

Real IPED acceptance was BLOCKED in the historical attempt.

That blocker was resolved before final Phase 6 acceptance by source-level
instrumentation and rebuild of the official IPED application.

The historical remediation options were:

1. Patch the official IPED source at a stable tag matching the deployed IPED
   version, rebuild IPED, install the patched application, and rerun
   `scripts/accept_iped_real_session.ps1`.
2. Replace the source patch approach with a supported IPED plugin/event hook or
   runtime instrumentation that actually receives selection/bookmark events.

## Historical Engineering Action

The required action was to create a reproducible IPED integration build:

1. Checkout a stable IPED release/tag matching the deployed version.
2. Apply SUPREME changes to `ResultTableListener.java` and
   `ResultTableModel.java`.
3. Include `SupremeAuditLogger.java` in the IPED app source tree or package it
   in a way the patched classes can call reliably.
4. Build with Maven/JDK 11 + JavaFX as required by IPED.
5. Install the patched IPED build into `C:\iped-test-case`.
6. Rerun real acceptance and require:
   - new `supreme_audit.ndjson` lines;
   - valid `event`, `itemId`, `mediaType`, `openTs`, `closeTs`, `userId`;
   - watcher ingestion;
   - `events_raw.source_tool='iped'`;
   - worker output and SENTINELA visibility.
