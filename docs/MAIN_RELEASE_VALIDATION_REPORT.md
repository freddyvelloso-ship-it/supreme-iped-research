# Main Release Validation Report

Date: 2026-06-29

Decision: `main_release_ready`

## Scope

This report records the final stabilization stack merge and clean-clone validation for `freddyvelloso-ship-it/supreme-iped-research`.

No feature work, UI redesign, real data, media, secrets, certificates, raw identifiers, raw paths, evidence hashes, or local outputs were added as part of this report.

## Merged PRs

The stabilization stack was merged in this order:

1. PR #1: `codex/system-health-publication-audit` -> `main`
   - Merge commit: `cd51dd62068ee509067dd87e3c3897c7172f884d`
2. PR #3: `codex/restore-sentinela-lab-ui` -> `main`
   - Retargeted from `codex/system-health-publication-audit` to `main` after PR #1 merged.
   - Merge commit: `05b7490ddc4a3060b1c0b665dbac48ea8763bd71`
3. PR #4: `codex/full-system-production-health-audit` -> `main`
   - Retargeted from `codex/restore-sentinela-lab-ui` to `main` after PR #3 merged.
   - Merge commit: `c09c06289d0ab1dd5b8482991a85217d218c0aa7`

Final `main` commit validated:

```text
c09c06289d0ab1dd5b8482991a85217d218c0aa7
```

## Tracking Checks

Commands executed on local `main`:

```powershell
git ls-files IPED-local
git ls-files .env supreme-backend/.env.production sentinela/.env.production certs/fullchain.pem certs/privkey.pem tmp
```

Results:

- `IPED-local`: zero tracked files.
- `.env`, production env files, certificates, and `tmp`: zero tracked files.

## Local Main Validation

Path:

```text
C:\Users\nunas\Documents\Codex\2026-06-27\co\work\supreme-iped-research
```

Commands executed:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\release_phase_zero_check.ps1
C:\Users\nunas\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m pytest -q
C:\Users\nunas\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m ruff check .
git diff --check
```

Results:

- Phase Zero: failed locally as expected because this development checkout contains ignored local artifacts on disk: `.env`, production env files, local TLS certificates, local Prometheus/Alertmanager files, and `tmp/pytest` audit outputs.
- Pytest: passed, 8 tests.
- Ruff: passed.
- Diff check: passed.

The local Phase Zero failure is not a Git tracking failure. It is caused by ignored development artifacts in the working directory.

## Clean Clone Release Validation

Clean clone path:

```text
C:\Users\nunas\Documents\Codex\2026-06-27\co\release-main-clean-check\supreme-iped-research
```

Branch:

```text
main
```

Commit:

```text
c09c06289d0ab1dd5b8482991a85217d218c0aa7
```

Commands executed:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\release_phase_zero_check.ps1
C:\Users\nunas\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m pytest -q
C:\Users\nunas\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m ruff check .
git diff --check
```

Results:

- Phase Zero: passed, 0 failures.
- Pytest: passed, 8 tests.
- Ruff: passed.
- Diff check: passed.

## CI Notes

During final stabilization, CI gate failures were corrected without feature changes:

- `release_phase_zero_check.ps1` now normalizes scanned paths for Windows/Linux compatibility.
- `phase4_scientific_validation_check.ps1`, `phase5_forensic_custody_check.ps1`, and `phase7_world_production_check.ps1` now invoke Python scripts through resolved portable paths.
- The `production-gates` CI job now installs the backend Python dependencies before running scientific/forensic gates.

Final PR #4 CI on commit `8c58f7f706b9aff53ace77b609f52e1188a5fc89` passed before merge.

## Final Status

Decision: `main_release_ready`

The merged `main` is stable in a clean clone. Phase Zero, pytest, ruff, and diff check pass from a clean checkout. Production/local environment files, certificates, `IPED-local`, and transient outputs are not tracked by Git.

Release packaging should be generated from a clean clone or from a working tree where ignored local artifacts have been removed or isolated.
