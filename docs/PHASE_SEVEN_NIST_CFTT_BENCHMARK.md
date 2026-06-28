# SUPREME V4 - NIST CFTT-Inspired Benchmark

This benchmark is inspired by NIST CFTT principles: repeatability, integrity,
traceability, deterministic replay and version comparability. It is not a NIST
certification.

The benchmark checks:

- Synthetic dataset digest reproducibility.
- Required validation scenarios.
- False positive and false negative limits.
- Stability and low-data-quality sensitivity.
- Algorithm version consistency.
- Hash-chain shape for input, processing, output and admin audit.
- Replay output presence and algorithm metadata.

Run:

```powershell
python scripts\phase7_nist_cftt_benchmark.py --root .
```

Output:

- `docs/phase7_benchmark/benchmark_report.json`

