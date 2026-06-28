from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "phase4_scientific_validation.py"


def _load_phase4_module():
    spec = importlib.util.spec_from_file_location("phase4_scientific_validation", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_phase4_dataset_generation_is_reproducible():
    phase4 = _load_phase4_module()
    first = phase4.build_dataset()
    second = phase4.build_dataset()

    assert first == second
    assert phase4.dataset_digest(first) == phase4.dataset_digest(second)
    assert {row["scenario"] for row in first if row["evaluation_window"]} == set(phase4.SCENARIOS)
    assert all(row["synthetic"] is True for row in first)


def test_phase4_metrics_are_reproducible_and_cover_required_axes():
    phase4 = _load_phase4_module()
    records = phase4.build_dataset()
    first = phase4.run_validation(records)
    second = phase4.run_validation(records)
    first["generated_at_utc"] = "REPRODUCIBLE_RUN_TIMESTAMP"
    second["generated_at_utc"] = "REPRODUCIBLE_RUN_TIMESTAMP"

    assert first == second
    assert first["seed"] == 424242
    assert first["algorithm_version"] == "SUPREME-ANALYTICS-1.0.0"
    assert set(first["classification_metrics"]["by_scenario"]) == set(phase4.SCENARIOS)
    assert "volume_stability" in first
    assert "low_quality_sensitivity" in first
    assert first["external_independent_validation"] == "not_performed"


def test_phase4_flag_metrics_have_no_synthetic_false_negatives_or_false_positives():
    phase4 = _load_phase4_module()
    metrics = phase4.run_validation(phase4.build_dataset())
    aggregate = metrics["classification_metrics"]["aggregate"]

    assert aggregate["false_positive_rate"] == 0.0
    assert aggregate["false_negative_rate"] == 0.0
    assert aggregate["f1"] == 1.0
