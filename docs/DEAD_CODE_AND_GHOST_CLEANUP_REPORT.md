# Dead Code And Ghost Cleanup Report

## Status

Decision: `cleanup_safe`

Branch: `codex/dead-code-and-ghost-cleanup`

Base used: `codex/system-health-publication-audit`

Reason for base choice: the publication health audit commit was still ahead of the local `main`, so this cleanup was based on that branch to preserve the recent login, i18n, IPED gate and test fixes.

## Scope

Files audited:

- `sentinela/static/index.html`
- `sentinela/static/sentinela-ux.js`
- `sentinela/static/sentinela-redesign.css`
- `scripts/iped_journey_gate.mjs`
- `LAUNCHER_IPED.ps1`
- `tests/test_publication_static_health.py`
- `tests/test_workspace_health.py`
- recent system health documentation

Searches used:

- dead wrapper patterns: `return ensure`, `return refresh`, `return enhance`
- temporary markers: `TODO`, `FIXME`, `debugger`
- stale UI strings: `View active`
- legacy login selectors: `login-card-scan`, `biometric-field`, `login-data-overlay`, `entry-brief`, `entry-assurance`, `bokeh-canvas`

## Dead Code Found

Confirmed dead code was found in `sentinela/static/sentinela-ux.js`.

The following wrapper functions returned immediately to the newer localized implementation, but still contained older unreachable code below the `return`:

- `ensureJurisdictionSwitch`
- `ensureTopbar`
- `refreshCommandCenter`
- `enhanceSectionLanguage`

That older code could never execute and duplicated behavior already handled by:

- `ensureLocalizedJurisdictionSwitch`
- `ensureLocalizedTopbar`
- `refreshLocalizedCommandCenter`
- `enhanceLocalizedSectionLanguage`

## Code Removed

Removed only the unreachable legacy bodies after the immediate `return` statements in `sentinela/static/sentinela-ux.js`.

No product behavior was intentionally changed. The active localized functions remain the execution path.

## Test Hardening Added

Added a static regression test in `tests/test_publication_static_health.py`:

- verifies the four localized wrapper functions still exist;
- verifies each wrapper is a single-line delegation;
- fails if unreachable legacy code is reintroduced after the `return`.

Also hardened `tests/test_workspace_health.py` by giving isolated pytest runs a unique `--basetemp` directory. This prevents Windows file-lock leftovers from making the workspace health suite fail while cleaning an old fixed temp directory.

## Legacy Kept By Design

The audit found old login-related selectors in CSS, including:

- `login-card-scan`
- `biometric-field`
- `login-data-overlay`
- `entry-brief`
- `entry-assurance`
- `bokeh-canvas`

These were not removed in this PR because some are defensive reset selectors in the current Sentinela Lab login layer and removing them would be a broader CSS cleanup. The active HTML does not include the old `login-card-scan` or `biometric-field` blocks, and existing tests enforce that.

## Items Left For Later

Potential future cleanup, not performed here:

- consolidate the large inline CSS/JS blocks in `sentinela/static/index.html`;
- split the Sentinela frontend into smaller static modules;
- audit historical docs and phase ledgers separately from runtime code;
- perform a CSS selector reachability pass with browser coverage before deleting broad presentation rules.

These are intentionally left out because the current PR is a controlled dead-code cleanup, not a visual refactor or feature cycle.

## Validation

Commands executed:

| Command | Result |
| --- | --- |
| `PYTHONPATH=src python -m pytest -q` | PASS, 8 passed |
| `python -m pytest -q` | PASS, 8 passed |
| `node --check sentinela/static/sentinela-ux.js` | PASS |
| `node --check scripts/iped_journey_gate.mjs` | PASS |
| `git diff --check` | PASS, only CRLF warnings |
| `docker compose -p supreme-v4-test-clone -f docker-compose.production.yml -f docker-compose.local.yml -f docker-compose.test-clone.yml ps` | PASS, local stack running |
| `python scripts/iped_operational_e2e.py --base-url http://127.0.0.1:18000 --require-sentinela --timeout-seconds 120` | PASS |
| `node scripts/iped_journey_gate.mjs --base-url http://127.0.0.1:18000` | PASS |
| Sentinela `/health` | PASS, HTTP 200 |
| Sentinela `/sentinela` | PASS, HTTP 200 |
| Sentinela login API | PASS, HTTP 200 |
| Sentinela `/api/auth/me` after login | PASS, HTTP 200 |

`ruff check .` was not executed successfully because `ruff` is not installed in this environment.

## Security And Guardrails

No real data, media, tokens, sensitive paths, raw identifiers, raw hashes or field exports were added.

The cleanup does not introduce:

- clinical diagnosis;
- individual ranking;
- productivity scoring;
- disciplinary recommendation;
- raw media/path exposure.

## Final Decision

`cleanup_safe`

The removed code was provably unreachable. Login, Sentinela, IPED gate, E2E flow and tests remain healthy after the cleanup.
