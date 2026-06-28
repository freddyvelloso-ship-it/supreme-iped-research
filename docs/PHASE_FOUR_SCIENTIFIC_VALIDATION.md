# SUPREME V4 - Phase 4 Scientific Validation Report

Status: internal synthetic scientific validation completed.

## Scope

This report validates reproducibility and expected behavior of the versioned
SUPREME analytic engine on deterministic synthetic data. It does not establish
clinical diagnosis, psychological assessment or automatic causal attribution.

Validation layers:

- Technical validation: automated deterministic tests and gates.
- Internal scientific validation: synthetic ground truth scenarios and metrics.
- External independent validation: not performed in this phase; required before
  broad scientific or regulatory claims.

## Reproducibility

- Seed: `424242`
- Algorithm version: `SUPREME-ANALYTICS-1.0.0`
- Dataset path: `docs/phase4_validation/synthetic_ground_truth_dataset.jsonl`
- Dataset digest: `845ef619dc74bc5fa30475a89e96ab044412ae3c6bf84370498cd37f728f17a3`
- Evaluation windows: `120`

## Scenario Metrics

| Scenario | Samples | False positive rate | False negative rate | Convergence match rate |
|---|---:|---:|---:|---:|
| `baixo_risco` | 24 | 0.000000 | 0.000000 | 1.000000 |
| `convergencia_critica` | 24 | 0.000000 | 0.000000 | 1.000000 |
| `cronicidade` | 24 | 0.000000 | 0.000000 | 1.000000 |
| `dissonancia` | 24 | 0.000000 | 0.000000 | 1.000000 |
| `reatividade` | 24 | 0.000000 | 0.000000 | 1.000000 |

## Aggregate Flag Metrics

- True positives: `72`
- False positives: `0`
- False negatives: `0`
- True negatives: `288`
- Precision: `1.000000`
- Recall: `1.000000`
- F1: `1.000000`
- False positive rate: `0.000000`
- False negative rate: `0.000000`

## Stability By Volume

| Samples per scenario | Evaluation windows | F1 | FP rate | FN rate | Mean IEO |
|---:|---:|---:|---:|---:|---:|
| 5 | 25 | 1.000000 | 0.000000 | 0.000000 | 0.468366 |
| 20 | 100 | 1.000000 | 0.000000 | 0.000000 | 0.467475 |
| 100 | 500 | 1.000000 | 0.000000 | 0.000000 | 0.467534 |

Max F1 delta: `0.000000`.

## Sensitivity To Low Data Quality Windows

| DQ score | F1 | FP rate | FN rate | Note |
|---:|---:|---:|---:|---|
| 1.0 | 1.000000 | 0.000000 | 0.000000 | DQ is carried as data-quality evidence; current analytic equations do not attenuate IEO by DQ. |
| 0.7 | 1.000000 | 0.000000 | 0.000000 | DQ is carried as data-quality evidence; current analytic equations do not attenuate IEO by DQ. |
| 0.4 | 1.000000 | 0.000000 | 0.000000 | DQ is carried as data-quality evidence; current analytic equations do not attenuate IEO by DQ. |

The current analytic equations carry DQ as evidence but do not attenuate IEO by
DQ. This is documented as a methodological limit for future validation.

## Limits

- Synthetic ground truth is engineered; it is not a substitute for external
  validation with authorized, ethically governed data.
- SUPREME outputs are decision-support evidence, not diagnosis.
- SUPREME outputs do not establish causal nexus automatically.
- Human review and institutional protocol remain required for individual action.
