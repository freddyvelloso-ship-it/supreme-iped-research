# LOCAL IPED Integration Check

Date: 2026-06-29

Latest local validation update: Docker Desktop is running and the full
`scripts\local.ps1 -Action all` workflow passed end-to-end.

## Local directories

- SUPREME-IPED Research: `C:\Users\nunas\Documents\Codex\2026-06-27\co\work\supreme-iped-research`
- IPED official source: `C:\Users\nunas\Documents\Codex\2026-06-27\co\work\IPED`
- Preserved partial clone from first timeout: `C:\Users\nunas\Documents\Codex\2026-06-27\co\work\supreme-iped-research-partial-20260629-095606`

## Repository state

| Repo | Branch | HEAD | Remote | Status |
|---|---:|---|---|---|
| SUPREME-IPED Research | `main` | `7e602846ec374ca9082e1827c32051e1a3a939b6` | `https://github.com/freddyvelloso-ship-it/supreme-iped-research` | clean except this local report and ignored local env files |
| IPED official | `master` | `961b8aa141e636566824d43c415cbc253500729c` | `https://github.com/sepinf-inc/IPED` | clean |

## Integration model found

SUPREME-IPED resolves IPED through:

- `IPED_HOME` environment variable;
- `scripts/verify_iped_real_environment.ps1 -IpedHome ...`;
- fallback runtime locations including `.\IPED-local\iped`;
- `supreme-iped-integration/launcher/*` launchers;
- `supreme-iped-integration/iped-patch/` Java patch docs and source.

The IPED integration expects an IPED runtime or patched build, not only the source tree. A valid runtime is detected when the target contains one of:

- `IPED-SearchApp.exe`;
- `bin\IPED-SearchApp.exe`;
- `iped.jar`;
- `iped-searchapp.jar`;
- `lib\iped-search-app.jar`;
- `iped-app*.jar`.

## Local configuration created

Created ignored local file:

- `.env.local`

Contents point to the external IPED source clone:

```text
IPED_HOME=C:\Users\nunas\Documents\Codex\2026-06-27\co\work\IPED
IPED_SOURCE_HOME=C:\Users\nunas\Documents\Codex\2026-06-27\co\work\IPED
```

Generated ignored local runtime files with `scripts\setup_env_local.ps1`:

- `.env`
- `supreme-backend\.env.production`
- `sentinela\.env.production`
- `infra\prometheus\supreme-api-token.local`
- `infra\alertmanager\alertmanager.yml`
- `tmp\iped-audit\`

No secret values are recorded in this report.

## Environment

| Tool | Result |
|---|---|
| Git | `2.54.0.windows.1` |
| Python | `3.12.13` |
| Java | OpenJDK `11.0.31` |
| Maven | Apache Maven `3.9.16` |
| Node | `v24.14.0` |
| Docker | running; Compose stack validated |

## Commands executed

### Clone and repo checks

| Command | Result |
|---|---|
| `git clone https://github.com/freddyvelloso-ship-it/supreme-iped-research supreme-iped-research` | timed out; partial clone preserved |
| `git clone https://github.com/freddyvelloso-ship-it/supreme-iped-research supreme-iped-research-clean` | passed; moved into final path |
| `git clone https://github.com/sepinf-inc/IPED IPED` | passed |
| `git status --short` in final SUPREME-IPED clone | clean before local env/report |
| `git status --short` in IPED clone | clean |

### IPED official source checks

| Command | Result |
|---|---|
| `mvn -q -DskipTests -N validate` in official IPED clone | passed |
| Check for `IPED-SearchApp.exe` in official IPED clone | not present |
| Check for `iped-app\target` in official IPED clone | not present |

Interpretation: the official IPED clone is source-only. It must be built before it can be used as an IPED runtime by SUPREME.

### SUPREME-IPED tests

| Command | Result |
|---|---|
| `python -m pytest supreme-iped-integration\tests -q` with workspace temp | passed: `46 passed` |
| `python -m pytest tests -q` from `supreme-backend` with `PYTHONPATH=.` | passed: `40 passed` |
| `python -m pytest tests -q` from `sentinela` with `PYTHONPATH=.` | passed: `28 passed` |

### Local Docker workflow

| Command | Result |
|---|---|
| `powershell -ExecutionPolicy Bypass -File scripts\local.ps1 -Action all -PythonExe C:\Users\nunas\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe` | passed |

Observed final E2E result:

```json
{
  "status": "ok",
  "events_stored_http": 8,
  "events_raw": 8,
  "window_metrics_at_least_4": true,
  "ieo_logs": 4,
  "sentinela_ieo_windows": 4,
  "pipeline_status": "ok",
  "redis_rq_analytics_observed": true
}
```

During validation, the local E2E scripts and sanitizer allowlist were aligned
with the hardened pseudonymized contract:

- E2E user identifiers are now SHA-256 hex pseudonyms.
- `ieo_linear`, `convergence_class` and `baseline_frozen` are accepted as safe
  analytical fields instead of being rejected by substring false positives.
- longitudinal profile evidence keeps the human-review guardrail without using
  forbidden diagnostic wording in the machine payload.

### IPED runtime checks

| Command | Result |
|---|---|
| `scripts\verify_iped_real_environment.ps1 -IpedHome .\IPED-local\iped -SkipDocker -ReportOnly` | passed with 0 failures, 1 warning: audit log will be created during real patched IPED session |
| `scripts\verify_iped_real_environment.ps1 -IpedHome C:\Users\nunas\Documents\Codex\2026-06-27\co\work\IPED -SkipDocker -ReportOnly` | source path is not a runtime; script fell through to installed `C:\iped-test-case` and passed |
| `scripts\production_readiness_check.ps1 -TemplateMode` | passed: 0 failures, 0 warnings |

### Release/audit check

| Command | Result |
|---|---|
| `scripts\phase_zero_audit.ps1` | failed |

Observed failures:

- mojibake in `README.md`;
- `IPED-local` present;
- nested ZIPs inside `IPED-local`.

Interpretation: this checkout is a research/field package with bundled IPED material, not a clean Phase Zero release package. The release gate correctly blocks this tree as a release artifact.

## What passed

- SUPREME-IPED clone created and usable.
- Official IPED clone created separately as a sibling directory.
- Local ignored env generated.
- `.env.local` points to the official IPED source clone.
- Python tests passed across integration, backend and Sentinela modules.
- The packaged `IPED-local\iped` runtime is detected and already instrumented with `SupremeAuditLogger`.
- Template production readiness check passed.
- IPED official source Maven root validation passed.

## Blockers

1. Official IPED clone is source-only.
   - Impact: `work\IPED` cannot be used as `IPED_HOME` runtime until built.
   - Fix:
     ```powershell
     cd C:\Users\nunas\Documents\Codex\2026-06-27\co\work\IPED
     C:\maven\apache-maven-3.9.16\bin\mvn.cmd clean install -DskipTests -T4
     ```
   - After applying the SUPREME patch and packaging, point `IPED_HOME` to the built runtime/release directory.

2. Real patched IPED session not executed in this cycle.
   - Impact: `tmp\iped-audit\supreme_audit.ndjson` has not yet been created by this local runtime.
   - Fix: run patched IPED and interact with a test case, then run:
     ```powershell
     powershell -ExecutionPolicy Bypass -File scripts\verify_iped_real_environment.ps1 -IpedHome .\IPED-local\iped -SkipDocker -ReportOnly
     ```

3. Phase Zero release audit fails on this checkout.
   - Impact: this tree should not be treated as a clean release artifact.
   - Fix: use the release packaging scripts that exclude local/bundled IPED artifacts, or clean the release package separately.

## Recommended next commands

Use bundled/instrumented IPED runtime for immediate local verification:

```powershell
cd C:\Users\nunas\Documents\Codex\2026-06-27\co\work\supreme-iped-research
powershell -ExecutionPolicy Bypass -File scripts\verify_iped_real_environment.ps1 -IpedHome .\IPED-local\iped -SkipDocker -ReportOnly
```

To rerun the full local workflow:

```powershell
cd C:\Users\nunas\Documents\Codex\2026-06-27\co\work\supreme-iped-research
powershell -ExecutionPolicy Bypass -File scripts\local.ps1 -Action all -PythonExe C:\Users\nunas\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe
```

For official IPED source build:

```powershell
cd C:\Users\nunas\Documents\Codex\2026-06-27\co\work\IPED
C:\maven\apache-maven-3.9.16\bin\mvn.cmd clean install -DskipTests -T4
```

## Sensitive data note

No real data was added. Generated env files and local tokens are ignored by Git and values are not printed here. No push or commit was performed.
