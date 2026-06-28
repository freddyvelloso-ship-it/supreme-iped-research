# SUPREME V4 - Technical Whitepaper

## Context

SUPREME V4 ingests operational evidence interaction events from IPED, computes
auditable exposure and psychometric convergence outputs in the backend, and
presents role-scoped evidence in SENTINELA.

## Architecture

IPED emits audit events. SUPREME signs, stores and processes events through
Postgres, Redis/RQ and the centralized analytics engine. SENTINELA is viewer-only
and consumes auditable outputs.

## Data Contract

Outputs carry `algorithm_version`, `algorithm_parameters`, participant scope,
window reference and integrity hashes where applicable.

## IEO, PSI and Red Flags

IEO, PSI and red flags are calculated only in SUPREME. SENTINELA does not
recalculate critical rules.

## Validation

Internal validation uses deterministic synthetic ground truth. External
independent validation is required before scientific claims beyond this package.

## Custody

Phase 5 provides signed events, hash chains, manifests, replay and forensic
exports.

## Security and LGPD

Phase 2 adds cookie sessions, RBAC, scope controls, readiness gates, secret scan,
dependency scan, SAST and SBOM.

## Limits

SUPREME V4 is not a clinical diagnostic tool, not a standalone psychological
assessment, and not an automatic causal nexus engine.

