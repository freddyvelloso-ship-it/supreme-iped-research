# Sentinela Lab UI Restore Report

## Decision

`sentinela_lab_ui_restored`

The Sentinela console in `supreme-iped-research` was restored so the SUPREME Lab visual layer is the primary authenticated interface. The older hybrid/legacy executable layer is no longer allowed to reappear after login, refresh, or navigation.

## Branch And Base

- Branch: `codex/restore-sentinela-lab-ui`
- Base branch: `codex/system-health-publication-audit`
- Target PR base: `codex/system-health-publication-audit`

## Reference Layer

Reference used from the SUPREME Lab visual language:

- authenticated institutional console layout;
- restrained light workspace with dark navigation shell;
- pseudonymized analytical status cards;
- operational dashboard framing;
- explicit governance and non-disciplinary guardrails.

No real data, media, raw paths, raw identifiers, raw evidence hashes, secrets, or field outputs were copied.

## Files Changed

- `sentinela/static/index.html`
  - Loads `sentinela-lab-primary.css` after the older stylesheets.
  - Loads the restored `sentinela-ux.js` with a new cache-buster.

- `sentinela/static/sentinela-lab-primary.css`
  - New final visual layer scoped to `body.sentinela-lab-primary`.
  - Hides legacy hybrid components that previously returned after login.
  - Restores a SUPREME Lab style navigation/header/dashboard shell.

- `sentinela/static/sentinela-ux.js`
  - Replaced the legacy hybrid UX layer with `SENTINELA_LAB_PRIMARY`.
  - Applies the new shell after login and after dashboard reload.
  - Removes old executable visual nodes.
  - Preserves existing login/session/endpoints/routes.
  - Preserves PT/EN/ES language switching.

- `tests/test_publication_static_health.py`
  - Verifies the primary layer is loaded and the legacy dashboard hook is not active.
  - Verifies PT/EN/ES hero copy.

- `sentinela/tests/test_phase6_product.py`
  - Verifies the product console keeps the primary layer active.
  - Verifies frontend section coverage and language copy.

- `tests/test_workspace_health.py`
  - Isolates temporary pytest workspace paths to avoid Windows stale temp directory collisions.

## Legacy Layers Disabled

The following legacy/hybrid elements are explicitly removed or hidden when the authenticated console starts:

- `ux-decision-panel`
- `ux-filter-brief`
- `ux-command-cycle`
- `foc-command-panels`
- `foc-zone-title`
- `foc-sidebar-brand`
- `foc-topbar-strip`
- `foc-jurisdiction-switch`

The previous `addDashboardUX` path is not present in the restored JS layer.

## Endpoint And Session Adaptation

The restore keeps the existing `supreme-iped-research` runtime contract:

- `/sentinela`
- `/health`
- `/api/auth/login`
- `/api/auth/me`
- `/api/dashboard/overview`
- `/api/dashboard/ieo-series`

The login/session flow is not replaced by SUPREME Lab code. Only the visual layer and safe dashboard shell are restored.

## Validation Executed

Commands executed:

```powershell
C:\Users\nunas\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe --check sentinela\static\sentinela-ux.js
C:\Users\nunas\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe --check scripts\iped_journey_gate.mjs
$env:PYTHONPATH='src'; C:\Users\nunas\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m pytest -q
C:\Users\nunas\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m pytest -q
git diff --check
```

Sentinela isolated product tests were also executed from `sentinela/`:

```powershell
$env:PYTHONPATH='src'; python -m pytest tests\test_phase6_product.py -q
```

Local runtime checks executed against the running Docker container:

- `/health`: HTTP 200
- `/sentinela`: HTTP 200
- `/api/auth/login`: HTTP 200
- `/api/auth/me`: HTTP 200
- `/api/dashboard/overview`: HTTP 200
- `/api/dashboard/ieo-series`: HTTP 200
- `/sentinela` contains `sentinela-lab-primary.css`
- `/sentinela` contains the restored `sentinela-ux.js` cache-buster
- `/sentinela` does not contain the old `addDashboardUX` hook

`ruff check .` was attempted, but `ruff` is not installed in this environment.

## Manual/Local Status

Expected local URL:

```text
http://localhost:18001/sentinela
```

Expected behavior:

- login opens the new Sentinela Lab visual layer;
- after login, Visao Geral remains in the new layer;
- refresh does not restore the old hybrid layout;
- navigation remains functional;
- language switching updates the principal UI labels;
- the login page and authenticated console do not overlap.

## Guardrails

Preserved:

- no real names;
- no sensitive paths;
- no media;
- no raw identifiers;
- no raw evidence hashes;
- no diagnosis;
- no ranking;
- no productivity scoring;
- no disciplinary recommendation.

## Remaining Notes

This PR restores the visual primary layer. It does not introduce new analytical metrics or change the IPED/SUPREME/Sentinela data model.
