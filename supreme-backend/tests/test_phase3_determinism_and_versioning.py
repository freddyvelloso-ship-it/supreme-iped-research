from __future__ import annotations

from datetime import date

from src.engine.supreme.algorithm import CURRENT_ALGORITHM_VERSION, algorithm_parameters
from src.engine.supreme.ieo import compute_ieo
from src.engine.supreme.models import BaselineParameters, IEORecord, WindowMetrics
from src.engine.supreme.psi import compute_psi
from src.engine.supreme.red_flags import PSIWindow, evaluate_red_flags


def test_phase3_full_analytic_output_is_deterministic_and_versioned():
    metrics = WindowMetrics(
        id_hash="phase3-subject",
        window_start=date(2026, 3, 1),
        t_minutes=130.0,
        e_events=64,
        v_volume=3300.0,
        d_density=0.52,
        dq_score=1.0,
    )
    baseline = BaselineParameters(
        id_hash="phase3-subject",
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

    first_ieo = compute_ieo(metrics, baseline)
    second_ieo = compute_ieo(metrics, baseline)
    assert first_ieo == second_ieo

    first_psi = compute_psi(
        dass_raw=30.0,
        olbi_raw=39.0,
        srq_raw=12.0,
        panas_neg_raw=20.0,
        mean_dass=20.0,
        sd_dass=10.0,
        mean_olbi=30.0,
        sd_olbi=5.0,
        mean_srq=8.0,
        sd_srq=4.0,
        mean_panas=15.0,
        sd_panas=5.0,
        oei_score=first_ieo.ieo_score,
    )
    second_psi = compute_psi(
        dass_raw=30.0,
        olbi_raw=39.0,
        srq_raw=12.0,
        panas_neg_raw=20.0,
        mean_dass=20.0,
        sd_dass=10.0,
        mean_olbi=30.0,
        sd_olbi=5.0,
        mean_srq=8.0,
        sd_srq=4.0,
        mean_panas=15.0,
        sd_panas=5.0,
        oei_score=first_ieo.ieo_score,
    )
    assert first_psi == second_psi

    current = PSIWindow(
        id_hash=metrics.id_hash,
        window_start=metrics.window_start,
        psi_score=first_psi.psi_score,
        z_dass=first_psi.z_dass,
        z_olbi=first_psi.z_olbi,
        z_srq=first_psi.z_srq,
        z_panas_neg=first_psi.z_panas_neg,
    )
    ieo_record = IEORecord(**first_ieo.model_dump())
    flags_a = evaluate_red_flags(ieo_record, current, [current])
    flags_b = evaluate_red_flags(ieo_record, current, [current])

    assert flags_a == flags_b
    assert first_psi.algorithm_version == CURRENT_ALGORITHM_VERSION
    assert all(flag.algorithm_version == CURRENT_ALGORITHM_VERSION for flag in flags_a)
    params = algorithm_parameters()
    assert params["version"] == CURRENT_ALGORITHM_VERSION
    assert "ieo" in params and "psi" in params and "red_flags" in params
