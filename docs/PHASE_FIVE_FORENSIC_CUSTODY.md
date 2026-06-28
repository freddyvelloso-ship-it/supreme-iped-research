# SUPREME V4 - Phase 5 Forensic Custody

Status: deterministic forensic custody package generated and verified for a simulated IPED event flow.

## Scope

This phase implements verifiable custody for synthetic/simulated IPED evidence and provides the same
manifest structure for real IPED sessions when an authorized real environment is available. No real IPED
case data is included in these artifacts.

Evidence types:

- Local simulated evidence: executed by `scripts/phase5_forensic_custody.py`.
- Real IPED evidence: supported by the manifest fields and real-environment acceptance scripts, but not
  executed in this Codex environment because no authorized real IPED session was provided.

## Custody Controls

- Events are signed at the first trusted SUPREME capture point.
- Input, processing, output and administrative audit records are protected by hash chains.
- Session manifest records IPED, patch, proxy, watcher, SUPREME, SENTINELA and algorithm versions.
- Deterministic replay reconstructs analytical outputs from signed event payloads.
- The verifier fails on signature, hash, manifest, version or replay divergence.

## Current Manifest

- Session ID: `phase5-simulated-iped-session-001`
- Evidence mode: `simulated_iped`
- Input chain tip: `018676727dd8bc2351fe95abe708c85f4edf5eadc9372c177ebf64a371731a73`
- Processing chain tip: `b2f3ccb8b61b3393438e0849642c0d08606138c50e42dc4e4d4d785b432b66ff`
- Output chain tip: `f4c8d0e6f736dd229930eeed6b1b3a5d4e9704d4191fd81e976296470d9bddd0`
- Admin audit chain tip: `be18c20f8498950e3563e7fad4a881a3f2138acf025690138f60a23500f8d893`
- Manifest hash: `2c7f269956e88ccb07898925b189ba259568da07c5a39ad1edc2843ab15e0fec`

## Integrity Report

- Signed events: `8`
- Outputs: `4`
- Replay digest: `34b1762004564e85b893a09b52a0e0a497eec3925481751ebe14ca084ca40beb`
- Algorithm version: `SUPREME-ANALYTICS-1.0.0`

## Verification Commands

```powershell
python scripts\phase5_forensic_custody.py check
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\phase5_forensic_custody_check.ps1 -Root .
```

## Limits

- These artifacts do not include real case data.
- Real IPED sessions require authorized local execution of the IPED environment acceptance scripts.
- Custody verification proves integrity and replayability of the captured data path; it does not prove
  clinical diagnosis or causal attribution.
