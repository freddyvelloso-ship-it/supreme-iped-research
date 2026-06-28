from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REQUIRED_SCENARIOS = {
    "baixo_risco",
    "reatividade",
    "dissonancia",
    "cronicidade",
    "convergencia_critica",
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_jsonl_digest(path: Path) -> str:
    records = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    payload = json.dumps(records, sort_keys=True, ensure_ascii=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def check_chain(chain: list[dict]) -> bool:
    if not chain:
        return False
    previous = "0" * 64
    for index, item in enumerate(chain):
        if item.get("index") != index:
            return False
        if item.get("previous_hash") != previous:
            return False
        chain_hash = item.get("chain_hash")
        if not isinstance(chain_hash, str) or len(chain_hash) != 64:
            return False
        previous = chain_hash
    return True


def run(root: Path, output: Path) -> dict:
    metrics_path = root / "docs" / "phase4_validation" / "validation_metrics.json"
    export_path = root / "docs" / "phase5_forensic" / "forensic_export.json"
    manifest_path = root / "docs" / "phase5_forensic" / "session_manifest.json"

    metrics = load_json(metrics_path)
    export = load_json(export_path)
    manifest = load_json(manifest_path)

    scenarios = set(metrics["dataset"]["scenarios"])
    aggregate = metrics["classification_metrics"]["aggregate"]
    chains = export["chains"]
    integrity_report = export.get("integrity_report", {})
    output_count = int(integrity_report.get("output_count", 0) or 0)
    algorithm_version = metrics["algorithm_version"]

    checks = {
        "reproducibility_dataset_digest": metrics["dataset"]["digest_sha256"]
        == canonical_jsonl_digest(root / metrics["dataset"]["path"]),
        "required_scenarios_present": REQUIRED_SCENARIOS.issubset(scenarios),
        "false_positive_rate_within_internal_target": aggregate["false_positive_rate"] <= 0.05,
        "false_negative_rate_within_internal_target": aggregate["false_negative_rate"] <= 0.05,
        "algorithm_version_consistent": manifest.get("versions", {}).get("algorithm") == algorithm_version,
        "input_hash_chain_valid_shape": check_chain(chains.get("input", [])),
        "processing_hash_chain_valid_shape": check_chain(chains.get("processing", [])),
        "output_hash_chain_valid_shape": check_chain(chains.get("output", [])),
        "admin_audit_hash_chain_valid_shape": check_chain(chains.get("admin_audit", [])),
        "deterministic_replay_outputs_present": output_count >= 1
        and len(integrity_report.get("replay_digest", "")) == 64,
        "all_outputs_have_algorithm_metadata": integrity_report.get("versions", {}).get("algorithm")
        == algorithm_version
        and len(integrity_report.get("algorithm_parameters_digest", "")) == 64,
        "forensic_export_digest_present": len(export.get("export_hash", "")) == 64,
    }
    status = "ok" if all(checks.values()) else "fail"
    report = {
        "benchmark": "SUPREME_PHASE7_NIST_CFTT_INSPIRED",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "algorithm_version": algorithm_version,
        "dataset_digest": metrics["dataset"]["digest_sha256"],
        "forensic_export_hash": export.get("export_hash"),
        "metrics": {
            "false_positive_rate": aggregate["false_positive_rate"],
            "false_negative_rate": aggregate["false_negative_rate"],
            "f1": aggregate["f1"],
            "stability_max_f1_delta": metrics["volume_stability"]["max_f1_delta"],
            "low_quality_max_f1_drop": metrics["low_quality_sensitivity"]["max_f1_drop_from_full_quality"],
        },
        "checks": checks,
        "limits": [
            "Benchmark is inspired by NIST CFTT principles; it is not a NIST certification.",
            "Synthetic ground truth is not clinical validation.",
            "External independent statistical review remains a production governance step.",
        ],
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--output", default="docs/phase7_benchmark/benchmark_report.json")
    args = parser.parse_args()
    report = run(Path(args.root).resolve(), Path(args.root).resolve() / args.output)
    print(json.dumps({"status": report["status"], "output": args.output, "f1": report["metrics"]["f1"]}))
    return 0 if report["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
