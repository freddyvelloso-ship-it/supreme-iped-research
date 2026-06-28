from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SUPREME_BACKEND = ROOT / "supreme-backend"
if str(SUPREME_BACKEND) not in sys.path:
    sys.path.insert(0, str(SUPREME_BACKEND))

from src.engine.supreme.algorithm import CURRENT_ALGORITHM_VERSION, algorithm_parameters
from src.engine.supreme.ieo import compute_ieo
from src.engine.supreme.models import BaselineParameters, IEORecord, WindowMetrics
from src.engine.supreme.psi import compute_psi
from src.engine.supreme.red_flags import PSIWindow, evaluate_red_flags


VALIDATION_SEED = 424242
OUTPUT_DIR = ROOT / "docs" / "phase4_validation"
DATASET_PATH = OUTPUT_DIR / "synthetic_ground_truth_dataset.jsonl"
METRICS_PATH = OUTPUT_DIR / "validation_metrics.json"
GROUND_TRUTH_PATH = OUTPUT_DIR / "GROUND_TRUTH.md"
REPORT_PATH = ROOT / "docs" / "PHASE_FOUR_SCIENTIFIC_VALIDATION.md"
MODEL_CARD_PATH = ROOT / "docs" / "MODEL_CARD_SUPREME.md"

FLAG_TYPES = ["reatividade", "dissonancia", "cronicidade"]
SCENARIOS = [
    "baixo_risco",
    "reatividade",
    "dissonancia",
    "cronicidade",
    "convergencia_critica",
]


@dataclass(frozen=True)
class ScenarioSpec:
    name: str
    previous_exposure_z: dict[str, float]
    current_exposure_z: dict[str, float]
    previous_psych_z: dict[str, float]
    current_psych_z: dict[str, float]
    expected_flags: list[str]
    expected_convergence_class: str
    ground_truth_rationale: str


def scenario_specs() -> dict[str, ScenarioSpec]:
    low_exp = {"z_t": 0.0, "z_e": 0.0, "z_v": 0.0, "z_d": 0.0}
    below_baseline_exp = {"z_t": -1.0, "z_e": -1.0, "z_v": -1.0, "z_d": -2.0}
    return {
        "baixo_risco": ScenarioSpec(
            name="baixo_risco",
            previous_exposure_z=below_baseline_exp,
            current_exposure_z=below_baseline_exp,
            previous_psych_z={"z_dass": -0.5, "z_olbi": -0.5, "z_srq": -0.5, "z_panas_neg": -0.5},
            current_psych_z={"z_dass": -0.5, "z_olbi": -0.5, "z_srq": -0.5, "z_panas_neg": -0.5},
            expected_flags=[],
            expected_convergence_class="baseline",
            ground_truth_rationale=(
                "Synthetic control: exposure and psychometrics are below baseline, with no elevated component."
            ),
        ),
        "reatividade": ScenarioSpec(
            name="reatividade",
            previous_exposure_z=low_exp,
            current_exposure_z={"z_t": 1.7, "z_e": 1.2, "z_v": 1.1, "z_d": 0.8},
            previous_psych_z={"z_dass": 0.2, "z_olbi": 0.2, "z_srq": 0.2, "z_panas_neg": -0.2},
            current_psych_z={"z_dass": 1.2, "z_olbi": 0.2, "z_srq": 0.2, "z_panas_neg": 1.2},
            expected_flags=["reatividade"],
            expected_convergence_class="convergence",
            ground_truth_rationale=(
                "High exposure with increased negative affect; DASS is elevated so this is not a dissonance case."
            ),
        ),
        "dissonancia": ScenarioSpec(
            name="dissonancia",
            previous_exposure_z=low_exp,
            current_exposure_z={"z_t": 1.7, "z_e": 1.4, "z_v": 1.0, "z_d": 0.8},
            previous_psych_z={"z_dass": 0.1, "z_olbi": 0.1, "z_srq": 0.1, "z_panas_neg": 0.0},
            current_psych_z={"z_dass": 0.1, "z_olbi": 0.1, "z_srq": 0.1, "z_panas_neg": 0.0},
            expected_flags=["dissonancia"],
            expected_convergence_class="convergence",
            ground_truth_rationale=(
                "High exposure signal while DASS, OLBI and SRQ remain below the psychometric high threshold."
            ),
        ),
        "cronicidade": ScenarioSpec(
            name="cronicidade",
            previous_exposure_z=low_exp,
            current_exposure_z={"z_t": 0.1, "z_e": 0.1, "z_v": 0.1, "z_d": 0.1},
            previous_psych_z={"z_dass": 0.2, "z_olbi": 1.2, "z_srq": 0.2, "z_panas_neg": 0.0},
            current_psych_z={"z_dass": 0.2, "z_olbi": 1.3, "z_srq": 0.2, "z_panas_neg": 0.0},
            expected_flags=["cronicidade"],
            expected_convergence_class="convergence",
            ground_truth_rationale=(
                "Repeated OLBI elevation across two windows while exposure remains below the exposure threshold."
            ),
        ),
        "convergencia_critica": ScenarioSpec(
            name="convergencia_critica",
            previous_exposure_z=low_exp,
            current_exposure_z={"z_t": 1.8, "z_e": 1.5, "z_v": 1.3, "z_d": 0.9},
            previous_psych_z={"z_dass": 0.2, "z_olbi": 0.2, "z_srq": 0.2, "z_panas_neg": 0.9},
            current_psych_z={"z_dass": 1.2, "z_olbi": 1.1, "z_srq": 1.1, "z_panas_neg": 0.8},
            expected_flags=[],
            expected_convergence_class="convergence",
            ground_truth_rationale=(
                "High exposure and elevated PSI components, without PANAS increase and without stable low psychometrics."
            ),
        ),
    }


def _jitter(index: int, salt: int, amplitude: float = 0.015) -> float:
    value = ((index * 37 + salt * 17 + VALIDATION_SEED) % 19) - 9
    return round((value / 9.0) * amplitude, 6)


def _baseline(subject_id: str) -> BaselineParameters:
    return BaselineParameters(
        id_hash=subject_id,
        mean_t=100.0,
        sd_t=20.0,
        mean_e=50.0,
        sd_e=10.0,
        mean_v=2500.0,
        sd_v=1000.0,
        mean_d=0.40,
        sd_d=0.10,
        baseline_window_count=4,
        baseline_status="active",
    )


def _metrics_from_z(subject_id: str, window_start: date, z: dict[str, float], dq_score: float) -> WindowMetrics:
    baseline = _baseline(subject_id)
    t_minutes = baseline.mean_t + z["z_t"] * baseline.sd_t
    e_events = round(baseline.mean_e + z["z_e"] * baseline.sd_e)
    v_volume = baseline.mean_v + z["z_v"] * baseline.sd_v
    d_density = baseline.mean_d + z["z_d"] * baseline.sd_d
    return WindowMetrics(
        id_hash=subject_id,
        window_start=window_start,
        t_minutes=round(t_minutes, 6),
        e_events=int(e_events),
        v_volume=round(v_volume, 6),
        d_density=round(d_density, 6),
        dq_score=dq_score,
    )


def _raw_from_psych_z(z: dict[str, float]) -> dict[str, float]:
    return {
        "dass_raw": 20.0 + z["z_dass"] * 10.0,
        "olbi_raw": 30.0 + z["z_olbi"] * 5.0,
        "srq_raw": 8.0 + z["z_srq"] * 4.0,
        "panas_neg_raw": 15.0 + z["z_panas_neg"] * 5.0,
    }


def _record(
    *,
    subject_id: str,
    scenario: str,
    window_index: int,
    exposure_z: dict[str, float],
    psych_z: dict[str, float],
    expected_flags: list[str],
    expected_convergence_class: str,
    rationale: str,
    evaluation_window: bool,
    dq_score: float,
) -> dict[str, Any]:
    start = date(2026, 1, 1 + (window_index - 1) * 14)
    metrics = _metrics_from_z(subject_id, start, exposure_z, dq_score)
    return {
        "dataset_version": "SUPREME-PHASE4-SYNTHETIC-1.0.0",
        "synthetic": True,
        "seed": VALIDATION_SEED,
        "algorithm_version": CURRENT_ALGORITHM_VERSION,
        "subject_id": subject_id,
        "scenario": scenario,
        "window_index": window_index,
        "window_start": start.isoformat(),
        "evaluation_window": evaluation_window,
        "dq_score": dq_score,
        "window_metrics": metrics.model_dump(mode="json"),
        "psychometric_z": psych_z,
        "psychometric_raw": _raw_from_psych_z(psych_z),
        "ground_truth": {
            "expected_flags": expected_flags,
            "expected_convergence_class": expected_convergence_class,
            "rationale": rationale,
        },
    }


def build_dataset(n_per_scenario: int = 24, dq_score: float = 1.0) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for scenario_name in SCENARIOS:
        spec = scenario_specs()[scenario_name]
        for index in range(n_per_scenario):
            subject_id = f"synthetic-phase4-{scenario_name}-{index:03d}"

            previous_psych = dict(spec.previous_psych_z)
            current_psych = dict(spec.current_psych_z)
            previous_exposure = dict(spec.previous_exposure_z)
            current_exposure = dict(spec.current_exposure_z)

            for salt, key in enumerate(["z_t", "z_e", "z_v", "z_d"], start=1):
                previous_exposure[key] = round(previous_exposure[key] + _jitter(index, salt, 0.01), 6)
                current_exposure[key] = round(current_exposure[key] + _jitter(index, salt + 4, 0.01), 6)
            for salt, key in enumerate(["z_dass", "z_olbi", "z_srq"], start=9):
                previous_psych[key] = round(previous_psych[key] + _jitter(index, salt, 0.01), 6)
                current_psych[key] = round(current_psych[key] + _jitter(index, salt + 4, 0.01), 6)

            if scenario_name == "reatividade":
                previous_psych["z_panas_neg"] = round(-0.25 + _jitter(index, 30, 0.01), 6)
                current_psych["z_panas_neg"] = round(1.20 + abs(_jitter(index, 31, 0.01)), 6)
            elif scenario_name == "convergencia_critica":
                previous_psych["z_panas_neg"] = round(0.90 + abs(_jitter(index, 32, 0.01)), 6)
                current_psych["z_panas_neg"] = round(0.80 - abs(_jitter(index, 33, 0.01)), 6)
            else:
                previous_psych["z_panas_neg"] = spec.previous_psych_z["z_panas_neg"]
                current_psych["z_panas_neg"] = spec.current_psych_z["z_panas_neg"]

            records.append(_record(
                subject_id=subject_id,
                scenario=scenario_name,
                window_index=1,
                exposure_z=previous_exposure,
                psych_z=previous_psych,
                expected_flags=[],
                expected_convergence_class="baseline",
                rationale="History/calibration window for the synthetic scenario.",
                evaluation_window=False,
                dq_score=dq_score,
            ))
            records.append(_record(
                subject_id=subject_id,
                scenario=scenario_name,
                window_index=2,
                exposure_z=current_exposure,
                psych_z=current_psych,
                expected_flags=list(spec.expected_flags),
                expected_convergence_class=spec.expected_convergence_class,
                rationale=spec.ground_truth_rationale,
                evaluation_window=True,
                dq_score=dq_score,
            ))
    return records


def dataset_digest(records: list[dict[str, Any]]) -> str:
    payload = json.dumps(records, sort_keys=True, ensure_ascii=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _compute_outputs(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        grouped[record["subject_id"]].append(record)

    outputs: list[dict[str, Any]] = []
    for subject_id, rows in grouped.items():
        history: list[PSIWindow] = []
        for record in sorted(rows, key=lambda r: r["window_start"]):
            metrics = WindowMetrics(**record["window_metrics"])
            baseline = _baseline(subject_id)
            ieo = compute_ieo(metrics, baseline)
            raw = record["psychometric_raw"]
            psi = compute_psi(
                dass_raw=raw["dass_raw"],
                olbi_raw=raw["olbi_raw"],
                srq_raw=raw["srq_raw"],
                panas_neg_raw=raw["panas_neg_raw"],
                mean_dass=20.0,
                sd_dass=10.0,
                mean_olbi=30.0,
                sd_olbi=5.0,
                mean_srq=8.0,
                sd_srq=4.0,
                mean_panas=15.0,
                sd_panas=5.0,
                oei_score=ieo.ieo_score,
            )
            current = PSIWindow(
                id_hash=subject_id,
                window_start=date.fromisoformat(record["window_start"]),
                psi_score=psi.psi_score,
                z_dass=psi.z_dass,
                z_olbi=psi.z_olbi,
                z_srq=psi.z_srq,
                z_panas_neg=psi.z_panas_neg,
                convergence_class=psi.convergence_class,
            )
            flags = evaluate_red_flags(IEORecord(**ieo.model_dump()), current, [*history, current])
            history.append(current)
            outputs.append({
                "subject_id": subject_id,
                "scenario": record["scenario"],
                "window_start": record["window_start"],
                "evaluation_window": record["evaluation_window"],
                "expected_flags": record["ground_truth"]["expected_flags"],
                "predicted_flags": sorted(flag.flag_type for flag in flags),
                "expected_convergence_class": record["ground_truth"]["expected_convergence_class"],
                "predicted_convergence_class": psi.convergence_class,
                "ieo_score": ieo.ieo_score,
                "psi_score": round(psi.psi_score, 6),
                "dq_score": record["dq_score"],
                "algorithm_version": CURRENT_ALGORITHM_VERSION,
            })
    return outputs


def _rates_for_outputs(outputs: list[dict[str, Any]]) -> dict[str, Any]:
    eval_outputs = [row for row in outputs if row["evaluation_window"]]
    by_scenario: dict[str, dict[str, Any]] = {}
    aggregate_counts = {"tp": 0, "fp": 0, "fn": 0, "tn": 0}

    for scenario in SCENARIOS:
        rows = [row for row in eval_outputs if row["scenario"] == scenario]
        counts = {"tp": 0, "fp": 0, "fn": 0, "tn": 0}
        for row in rows:
            expected = set(row["expected_flags"])
            predicted = set(row["predicted_flags"])
            for flag_type in FLAG_TYPES:
                if flag_type in expected and flag_type in predicted:
                    counts["tp"] += 1
                elif flag_type not in expected and flag_type in predicted:
                    counts["fp"] += 1
                elif flag_type in expected and flag_type not in predicted:
                    counts["fn"] += 1
                else:
                    counts["tn"] += 1
        for key in aggregate_counts:
            aggregate_counts[key] += counts[key]
        fp_denom = counts["fp"] + counts["tn"]
        fn_denom = counts["fn"] + counts["tp"]
        convergence_matches = sum(
            row["expected_convergence_class"] == row["predicted_convergence_class"]
            for row in rows
        )
        by_scenario[scenario] = {
            "samples": len(rows),
            **counts,
            "false_positive_rate": round(counts["fp"] / fp_denom, 6) if fp_denom else 0.0,
            "false_negative_rate": round(counts["fn"] / fn_denom, 6) if fn_denom else 0.0,
            "convergence_match_rate": round(convergence_matches / len(rows), 6) if rows else 0.0,
        }

    precision = aggregate_counts["tp"] / max(aggregate_counts["tp"] + aggregate_counts["fp"], 1)
    recall = aggregate_counts["tp"] / max(aggregate_counts["tp"] + aggregate_counts["fn"], 1)
    f1 = 2 * precision * recall / max(precision + recall, 1e-12)
    aggregate = {
        **aggregate_counts,
        "precision": round(precision, 6),
        "recall": round(recall, 6),
        "f1": round(f1, 6),
        "false_positive_rate": round(
            aggregate_counts["fp"] / max(aggregate_counts["fp"] + aggregate_counts["tn"], 1), 6
        ),
        "false_negative_rate": round(
            aggregate_counts["fn"] / max(aggregate_counts["fn"] + aggregate_counts["tp"], 1), 6
        ),
    }
    return {"aggregate": aggregate, "by_scenario": by_scenario}


def _volume_stability() -> dict[str, Any]:
    levels = [5, 20, 100]
    rows = []
    for level in levels:
        records = build_dataset(n_per_scenario=level)
        outputs = _compute_outputs(records)
        rates = _rates_for_outputs(outputs)
        eval_outputs = [row for row in outputs if row["evaluation_window"]]
        rows.append({
            "samples_per_scenario": level,
            "total_evaluation_windows": len(eval_outputs),
            "f1": rates["aggregate"]["f1"],
            "false_positive_rate": rates["aggregate"]["false_positive_rate"],
            "false_negative_rate": rates["aggregate"]["false_negative_rate"],
            "mean_ieo_score": round(sum(row["ieo_score"] for row in eval_outputs) / len(eval_outputs), 6),
            "mean_psi_score": round(sum(row["psi_score"] for row in eval_outputs) / len(eval_outputs), 6),
        })
    return {
        "levels": rows,
        "max_f1_delta": round(max(row["f1"] for row in rows) - min(row["f1"] for row in rows), 6),
        "max_false_positive_rate_delta": round(
            max(row["false_positive_rate"] for row in rows) -
            min(row["false_positive_rate"] for row in rows), 6
        ),
    }


def _low_quality_sensitivity() -> dict[str, Any]:
    quality_levels = [1.0, 0.7, 0.4]
    rows = []
    baseline_f1 = None
    for dq in quality_levels:
        records = build_dataset(n_per_scenario=24, dq_score=dq)
        outputs = _compute_outputs(records)
        rates = _rates_for_outputs(outputs)
        f1 = rates["aggregate"]["f1"]
        if baseline_f1 is None:
            baseline_f1 = f1
        rows.append({
            "dq_score": dq,
            "f1": f1,
            "false_positive_rate": rates["aggregate"]["false_positive_rate"],
            "false_negative_rate": rates["aggregate"]["false_negative_rate"],
            "note": "DQ is carried as data-quality evidence; current analytic equations do not attenuate IEO by DQ.",
        })
    return {
        "quality_levels": rows,
        "max_f1_drop_from_full_quality": round((baseline_f1 or 0.0) - min(row["f1"] for row in rows), 6),
    }


def run_validation(records: list[dict[str, Any]]) -> dict[str, Any]:
    outputs = _compute_outputs(records)
    rates = _rates_for_outputs(outputs)
    return {
        "validation_version": "SUPREME-PHASE4-VALIDATION-1.0.0",
        "validation_type": "internal_synthetic_scientific_validation",
        "external_independent_validation": "not_performed",
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "seed": VALIDATION_SEED,
        "algorithm_version": CURRENT_ALGORITHM_VERSION,
        "algorithm_parameters": algorithm_parameters(),
        "dataset": {
            "path": str(DATASET_PATH.relative_to(ROOT)).replace("\\", "/"),
            "digest_sha256": dataset_digest(records),
            "records": len(records),
            "evaluation_windows": sum(1 for row in records if row["evaluation_window"]),
            "scenarios": SCENARIOS,
        },
        "classification_metrics": rates,
        "volume_stability": _volume_stability(),
        "low_quality_sensitivity": _low_quality_sensitivity(),
        "limits": [
            "Synthetic ground truth is engineered for internal validation and is not clinical validation.",
            "The outputs are not diagnosis, psychological assessment or automatic causal attribution.",
            "External independent statistical and domain review remains required before scientific claims.",
        ],
    }


def write_dataset(records: list[dict[str, Any]]) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with DATASET_PATH.open("w", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(json.dumps(record, sort_keys=True, ensure_ascii=True) + "\n")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    stable_payload = dict(payload)
    stable_payload["generated_at_utc"] = "REPRODUCIBLE_RUN_TIMESTAMP"
    path.write_text(
        json.dumps(stable_payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def render_ground_truth(records: list[dict[str, Any]]) -> str:
    scenario_rows = []
    specs = scenario_specs()
    for scenario in SCENARIOS:
        spec = specs[scenario]
        scenario_rows.append(
            f"| `{scenario}` | `{', '.join(spec.expected_flags) or 'none'}` | "
            f"`{spec.expected_convergence_class}` | {spec.ground_truth_rationale} |"
        )
    return "\n".join([
        "# SUPREME V4 Phase 4 - Synthetic Ground Truth",
        "",
        "This dataset is synthetic and deterministic. It contains no real IPED data, no real",
        "participant data and no operational secrets.",
        "",
        f"- Seed: `{VALIDATION_SEED}`",
        f"- Algorithm version: `{CURRENT_ALGORITHM_VERSION}`",
        f"- Records: `{len(records)}`",
        f"- Dataset digest: `{dataset_digest(records)}`",
        "",
        "| Scenario | Expected flags | Expected convergence class | Ground truth rationale |",
        "|---|---:|---:|---|",
        *scenario_rows,
        "",
        "Boundary of evidence: this is internal synthetic validation. It is useful for",
        "reproducibility, regression control and plausibility checks; it is not external",
        "clinical, epidemiological or causal validation.",
        "",
    ])


def render_report(metrics: dict[str, Any]) -> str:
    by_scenario = metrics["classification_metrics"]["by_scenario"]
    aggregate = metrics["classification_metrics"]["aggregate"]
    scenario_rows = [
        f"| `{name}` | {row['samples']} | {row['false_positive_rate']:.6f} | "
        f"{row['false_negative_rate']:.6f} | {row['convergence_match_rate']:.6f} |"
        for name, row in by_scenario.items()
    ]
    volume_rows = [
        f"| {row['samples_per_scenario']} | {row['total_evaluation_windows']} | "
        f"{row['f1']:.6f} | {row['false_positive_rate']:.6f} | "
        f"{row['false_negative_rate']:.6f} | {row['mean_ieo_score']:.6f} |"
        for row in metrics["volume_stability"]["levels"]
    ]
    quality_rows = [
        f"| {row['dq_score']:.1f} | {row['f1']:.6f} | "
        f"{row['false_positive_rate']:.6f} | {row['false_negative_rate']:.6f} | {row['note']} |"
        for row in metrics["low_quality_sensitivity"]["quality_levels"]
    ]
    return "\n".join([
        "# SUPREME V4 - Phase 4 Scientific Validation Report",
        "",
        "Status: internal synthetic scientific validation completed.",
        "",
        "## Scope",
        "",
        "This report validates reproducibility and expected behavior of the versioned",
        "SUPREME analytic engine on deterministic synthetic data. It does not establish",
        "clinical diagnosis, psychological assessment or automatic causal attribution.",
        "",
        "Validation layers:",
        "",
        "- Technical validation: automated deterministic tests and gates.",
        "- Internal scientific validation: synthetic ground truth scenarios and metrics.",
        "- External independent validation: not performed in this phase; required before",
        "  broad scientific or regulatory claims.",
        "",
        "## Reproducibility",
        "",
        f"- Seed: `{metrics['seed']}`",
        f"- Algorithm version: `{metrics['algorithm_version']}`",
        f"- Dataset path: `{metrics['dataset']['path']}`",
        f"- Dataset digest: `{metrics['dataset']['digest_sha256']}`",
        f"- Evaluation windows: `{metrics['dataset']['evaluation_windows']}`",
        "",
        "## Scenario Metrics",
        "",
        "| Scenario | Samples | False positive rate | False negative rate | Convergence match rate |",
        "|---|---:|---:|---:|---:|",
        *scenario_rows,
        "",
        "## Aggregate Flag Metrics",
        "",
        f"- True positives: `{aggregate['tp']}`",
        f"- False positives: `{aggregate['fp']}`",
        f"- False negatives: `{aggregate['fn']}`",
        f"- True negatives: `{aggregate['tn']}`",
        f"- Precision: `{aggregate['precision']:.6f}`",
        f"- Recall: `{aggregate['recall']:.6f}`",
        f"- F1: `{aggregate['f1']:.6f}`",
        f"- False positive rate: `{aggregate['false_positive_rate']:.6f}`",
        f"- False negative rate: `{aggregate['false_negative_rate']:.6f}`",
        "",
        "## Stability By Volume",
        "",
        "| Samples per scenario | Evaluation windows | F1 | FP rate | FN rate | Mean IEO |",
        "|---:|---:|---:|---:|---:|---:|",
        *volume_rows,
        "",
        f"Max F1 delta: `{metrics['volume_stability']['max_f1_delta']:.6f}`.",
        "",
        "## Sensitivity To Low Data Quality Windows",
        "",
        "| DQ score | F1 | FP rate | FN rate | Note |",
        "|---:|---:|---:|---:|---|",
        *quality_rows,
        "",
        "The current analytic equations carry DQ as evidence but do not attenuate IEO by",
        "DQ. This is documented as a methodological limit for future validation.",
        "",
        "## Limits",
        "",
        "- Synthetic ground truth is engineered; it is not a substitute for external",
        "  validation with authorized, ethically governed data.",
        "- SUPREME outputs are decision-support evidence, not diagnosis.",
        "- SUPREME outputs do not establish causal nexus automatically.",
        "- Human review and institutional protocol remain required for individual action.",
        "",
    ])


def render_model_card(metrics: dict[str, Any]) -> str:
    aggregate = metrics["classification_metrics"]["aggregate"]
    return "\n".join([
        "# SUPREME V4 Model Card",
        "",
        "## Model Identity",
        "",
        f"- Model/system: SUPREME V4 analytic engine",
        f"- Algorithm version: `{metrics['algorithm_version']}`",
        f"- Validation artifact version: `{metrics['validation_version']}`",
        f"- Seed: `{metrics['seed']}`",
        "",
        "## Intended Use",
        "",
        "SUPREME V4 produces occupational exposure and psychometric pressure indicators",
        "for governed research, audit and operational monitoring contexts. It is intended",
        "to support responsible review, not to replace professional judgment.",
        "",
        "## Out Of Scope",
        "",
        "- Clinical diagnosis.",
        "- Psychological assessment as a standalone instrument.",
        "- Automatic causal nexus.",
        "- Automated individual employment, medical or disciplinary decisions.",
        "",
        "## Inputs",
        "",
        "- Synthetic validation inputs: window-level exposure metrics and psychometric",
        "  z-scores generated by deterministic scripts.",
        "- Production inputs, when authorized: governed operational event aggregates and",
        "  psychometric submissions processed by the SUPREME backend.",
        "",
        "## Outputs",
        "",
        "- IEO, PSI, convergence class and typed red flags.",
        "- Algorithm version and algorithm parameters for auditability.",
        "",
        "## Internal Synthetic Validation Summary",
        "",
        f"- Dataset digest: `{metrics['dataset']['digest_sha256']}`",
        f"- Evaluation windows: `{metrics['dataset']['evaluation_windows']}`",
        f"- Aggregate precision: `{aggregate['precision']:.6f}`",
        f"- Aggregate recall: `{aggregate['recall']:.6f}`",
        f"- Aggregate F1: `{aggregate['f1']:.6f}`",
        f"- False positive rate: `{aggregate['false_positive_rate']:.6f}`",
        f"- False negative rate: `{aggregate['false_negative_rate']:.6f}`",
        "",
        "## Validation Boundaries",
        "",
        "Technical validation and internal synthetic validation are complete for Phase 4.",
        "External independent statistical review and domain validation are not complete",
        "in this phase and must precede market-level scientific claims.",
        "",
        "## Ethical And Scientific Limits",
        "",
        "- Results must be interpreted by authorized professionals under approved protocol.",
        "- The model may be sensitive to data collection quality and baseline quality.",
        "- Synthetic performance does not guarantee real-world performance.",
        "- No output should be treated as clinical or causal proof.",
        "",
    ])


def write_docs(records: list[dict[str, Any]], metrics: dict[str, Any]) -> None:
    GROUND_TRUTH_PATH.write_text(render_ground_truth(records), encoding="utf-8")
    REPORT_PATH.write_text(render_report(metrics), encoding="utf-8")
    MODEL_CARD_PATH.write_text(render_model_card(metrics), encoding="utf-8")


def run_all() -> dict[str, Any]:
    records = build_dataset()
    metrics = run_validation(records)
    write_dataset(records)
    write_json(METRICS_PATH, metrics)
    stored_metrics = json.loads(METRICS_PATH.read_text(encoding="utf-8"))
    write_docs(records, stored_metrics)
    return stored_metrics


def check_outputs() -> None:
    required = [DATASET_PATH, METRICS_PATH, GROUND_TRUTH_PATH, REPORT_PATH, MODEL_CARD_PATH]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.exists()]
    if missing:
        raise SystemExit(f"Missing Phase 4 validation artifacts: {missing}")
    records = load_jsonl(DATASET_PATH)
    fresh = run_validation(records)
    fresh["generated_at_utc"] = "REPRODUCIBLE_RUN_TIMESTAMP"
    stored = json.loads(METRICS_PATH.read_text(encoding="utf-8"))
    if stored != fresh:
        raise SystemExit("Stored Phase 4 metrics differ from deterministic recomputation.")
    if stored["algorithm_version"] != CURRENT_ALGORITHM_VERSION:
        raise SystemExit("Stored algorithm version does not match current SUPREME algorithm.")


def main() -> int:
    parser = argparse.ArgumentParser(description="SUPREME V4 Phase 4 scientific validation")
    parser.add_argument("action", choices=["all", "generate", "validate", "docs", "check"])
    args = parser.parse_args()

    if args.action == "all":
        metrics = run_all()
        print(json.dumps({
            "status": "ok",
            "dataset_digest": metrics["dataset"]["digest_sha256"],
            "f1": metrics["classification_metrics"]["aggregate"]["f1"],
            "false_positive_rate": metrics["classification_metrics"]["aggregate"]["false_positive_rate"],
            "false_negative_rate": metrics["classification_metrics"]["aggregate"]["false_negative_rate"],
        }, sort_keys=True))
        return 0
    if args.action == "generate":
        records = build_dataset()
        write_dataset(records)
        GROUND_TRUTH_PATH.write_text(render_ground_truth(records), encoding="utf-8")
        print(json.dumps({"status": "ok", "records": len(records), "digest": dataset_digest(records)}, sort_keys=True))
        return 0
    if args.action == "validate":
        records = load_jsonl(DATASET_PATH) if DATASET_PATH.exists() else build_dataset()
        metrics = run_validation(records)
        write_json(METRICS_PATH, metrics)
        print(json.dumps({"status": "ok", "metrics": str(METRICS_PATH.relative_to(ROOT))}, sort_keys=True))
        return 0
    if args.action == "docs":
        records = load_jsonl(DATASET_PATH)
        metrics = json.loads(METRICS_PATH.read_text(encoding="utf-8"))
        write_docs(records, metrics)
        print(json.dumps({"status": "ok", "report": str(REPORT_PATH.relative_to(ROOT))}, sort_keys=True))
        return 0
    if args.action == "check":
        check_outputs()
        print(json.dumps({"status": "ok", "check": "phase4 scientific validation reproducible"}, sort_keys=True))
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
