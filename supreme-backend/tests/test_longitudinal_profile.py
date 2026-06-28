from __future__ import annotations

from datetime import date, datetime, timezone

from src.engine.supreme.algorithm import CURRENT_ALGORITHM_VERSION
from src.engine.supreme.longitudinal_profile import (
    ProfileFlag,
    ProfileWindow,
    classify_longitudinal_profile,
)
from src.engine.supreme.models import BaselineParameters


def _baseline(count: int = 8) -> BaselineParameters:
    return BaselineParameters(
        id_hash="profile-subject",
        mean_t=100.0,
        sd_t=20.0,
        mean_e=50.0,
        sd_e=10.0,
        mean_v=2500.0,
        sd_v=900.0,
        mean_d=0.40,
        sd_d=0.10,
        baseline_window_count=count,
        baseline_version=2,
        baseline_frozen_at=datetime(2026, 2, 1, tzinfo=timezone.utc),
        baseline_status="active",
    )


def _windows(ieo: list[float], psi: list[float] | None = None) -> list[ProfileWindow]:
    psi_values = psi or [0.2 for _ in ieo]
    return [
        ProfileWindow(
            window_start=date(2026, 1, 1 + index),
            ieo_score=ieo_score,
            psi_score=psi_values[index],
            dq_score=0.9,
            convergence_class="baseline",
        )
        for index, ieo_score in enumerate(ieo)
    ]


def test_profile_medio_when_no_extreme_pattern():
    result = classify_longitudinal_profile(
        "profile-subject",
        _baseline(count=6),
        _windows([0.35, 0.40, 0.42, 0.43], [0.35, 0.38, 0.40, 0.42]),
        [],
    )

    assert result.profile_class == "medio"
    assert result.profile_label == "Médio"


def test_profile_resiliente_for_high_exposure_low_psychometric_load():
    result = classify_longitudinal_profile(
        "profile-subject",
        _baseline(count=8),
        _windows([0.70, 0.72, 0.75, 0.74], [0.10, 0.12, 0.14, 0.16]),
        [],
    )

    assert result.profile_class == "resiliente"


def test_profile_vulneravel_for_persistent_flags_or_high_psi():
    result = classify_longitudinal_profile(
        "profile-subject",
        _baseline(count=8),
        _windows([0.30, 0.35, 0.42, 0.45], [0.55, 0.70, 0.90, 1.05]),
        [ProfileFlag(date(2026, 1, 4), "cronicidade", "maior")],
    )

    assert result.profile_class == "vulneravel"


def test_profile_junior_for_early_high_variability_pattern():
    result = classify_longitudinal_profile(
        "profile-subject",
        _baseline(count=4),
        _windows([0.15, 0.85, 0.18, 0.88], [0.20, 0.20, 0.22, 0.21]),
        [],
    )

    assert result.profile_class == "junior"


def test_profile_senior_for_stable_low_load_long_history():
    result = classify_longitudinal_profile(
        "profile-subject",
        _baseline(count=8),
        _windows([0.30, 0.31, 0.32, 0.32, 0.33, 0.34, 0.35, 0.36], [0.18] * 8),
        [],
    )

    assert result.profile_class == "senior"


def test_profile_provisional_medio_when_history_is_insufficient():
    result = classify_longitudinal_profile(
        "profile-subject",
        None,
        _windows([0.70, 0.80], [0.90, 1.00]),
        [],
    )

    assert result.profile_class == "medio"
    assert result.profile_confidence == 0.25
    assert result.profile_evidence["provisional"] is True


def test_profile_is_deterministic_and_versioned():
    baseline = _baseline(count=8)
    windows = _windows([0.30, 0.31, 0.32, 0.32, 0.33, 0.34, 0.35, 0.36], [0.18] * 8)
    flags: list[ProfileFlag] = []
    fixed_time = datetime(2026, 6, 1, tzinfo=timezone.utc)

    first = classify_longitudinal_profile("profile-subject", baseline, windows, flags, fixed_time)
    second = classify_longitudinal_profile("profile-subject", baseline, windows, flags, fixed_time)

    assert first == second
    assert first.algorithm_version == CURRENT_ALGORITHM_VERSION
    assert "longitudinal_profile" in first.algorithm_parameters
