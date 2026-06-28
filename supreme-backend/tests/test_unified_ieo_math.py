from __future__ import annotations

from datetime import date

from src.engine.supreme.algorithm import CURRENT_ALGORITHM_VERSION, algorithm_parameters
from src.engine.supreme.ieo import compute_ieo, ieo_final, ieo_linear, ieo_saturation
from src.engine.supreme.models import BaselineParameters, WindowMetrics, ZScores


def test_ieo_math_is_deterministic_and_versioned():
    z = ZScores(z_t=2.0, z_e=1.0, z_v=0.5, z_d=1.5)

    linear = ieo_linear(z)
    saturation = ieo_saturation(linear)
    final = ieo_final(saturation, z.z_d)

    assert round(linear, 6) == 1.4
    assert round(saturation, 6) == 0.598688
    assert round(final, 6) == 0.748688
    assert CURRENT_ALGORITHM_VERSION == "SUPREME-ANALYTICS-1.0.0"
    assert algorithm_parameters()["ieo"]["z_t"] == 0.5


def test_compute_ieo_same_input_same_output():
    metrics = WindowMetrics(
        id_hash="subject-1",
        window_start=date(2026, 1, 15),
        t_minutes=120.0,
        e_events=60,
        v_volume=3000.0,
        d_density=0.5,
        dq_score=1.0,
    )
    baseline = BaselineParameters(
        id_hash="subject-1",
        mean_t=100.0,
        sd_t=10.0,
        mean_e=50.0,
        sd_e=10.0,
        mean_v=2500.0,
        sd_v=1000.0,
        mean_d=0.35,
        sd_d=0.1,
        baseline_window_count=4,
        baseline_status="active",
    )

    first = compute_ieo(metrics, baseline)
    second = compute_ieo(metrics, baseline)

    assert first == second
    assert first.ieo_score == 0.748688
    assert first.z_t == 2.0
    assert first.z_e == 1.0
    assert first.z_v == 0.5
    assert first.z_d == 1.5
