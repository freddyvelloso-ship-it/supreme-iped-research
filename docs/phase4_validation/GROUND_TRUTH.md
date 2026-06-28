# SUPREME V4 Phase 4 - Synthetic Ground Truth

This dataset is synthetic and deterministic. It contains no real IPED data, no real
participant data and no operational secrets.

- Seed: `424242`
- Algorithm version: `SUPREME-ANALYTICS-1.0.0`
- Records: `240`
- Dataset digest: `845ef619dc74bc5fa30475a89e96ab044412ae3c6bf84370498cd37f728f17a3`

| Scenario | Expected flags | Expected convergence class | Ground truth rationale |
|---|---:|---:|---|
| `baixo_risco` | `none` | `baseline` | Synthetic control: exposure and psychometrics are below baseline, with no elevated component. |
| `reatividade` | `reatividade` | `convergence` | High exposure with increased negative affect; DASS is elevated so this is not a dissonance case. |
| `dissonancia` | `dissonancia` | `convergence` | High exposure signal while DASS, OLBI and SRQ remain below the psychometric high threshold. |
| `cronicidade` | `cronicidade` | `convergence` | Repeated OLBI elevation across two windows while exposure remains below the exposure threshold. |
| `convergencia_critica` | `none` | `convergence` | High exposure and elevated PSI components, without PANAS increase and without stable low psychometrics. |

Boundary of evidence: this is internal synthetic validation. It is useful for
reproducibility, regression control and plausibility checks; it is not external
clinical, epidemiological or causal validation.
