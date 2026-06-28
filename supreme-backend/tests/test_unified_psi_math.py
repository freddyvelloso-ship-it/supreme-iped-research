from __future__ import annotations

from src.engine.supreme.algorithm import CURRENT_ALGORITHM_VERSION, algorithm_parameters
from src.engine.supreme.psi import compute_psi


def test_psi_math_is_weighted_deterministic_and_versioned():
    result = compute_psi(
        dass_raw=30.0,
        olbi_raw=40.0,
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
        oei_score=1.2,
    )

    assert round(result.z_dass, 6) == 1.0
    assert round(result.z_olbi, 6) == 2.0
    assert round(result.z_srq, 6) == 1.0
    assert round(result.z_panas_neg, 6) == 1.0
    assert round(result.psi_score, 6) == 1.2
    assert result.convergence_class == "convergence"
    assert result.algorithm_version == CURRENT_ALGORITHM_VERSION
    assert algorithm_parameters()["psi"]["z_panas_neg"] == 0.4
    assert algorithm_parameters()["psi"]["z_olbi"] == 0.2


def test_psi_prioritizes_panas_negative_as_acute_sensor():
    result = compute_psi(
        dass_raw=20.0,
        olbi_raw=30.0,
        srq_raw=8.0,
        panas_neg_raw=22.5,
        mean_dass=20.0,
        sd_dass=10.0,
        mean_olbi=30.0,
        sd_olbi=5.0,
        mean_srq=8.0,
        sd_srq=4.0,
        mean_panas=15.0,
        sd_panas=5.0,
        oei_score=0.0,
    )

    assert round(result.z_panas_neg, 6) == 1.5
    assert round(result.psi_score, 6) == 0.6


def test_psi_classifies_divergence_when_ieo_high_and_psi_not_high():
    result = compute_psi(
        dass_raw=20.0,
        olbi_raw=30.0,
        srq_raw=8.0,
        panas_neg_raw=15.0,
        mean_dass=20.0,
        sd_dass=10.0,
        mean_olbi=30.0,
        sd_olbi=5.0,
        mean_srq=8.0,
        sd_srq=4.0,
        mean_panas=15.0,
        sd_panas=5.0,
        oei_score=0.8,
    )

    assert result.psi_score == 0.0
    assert result.convergence_class == "divergence"
