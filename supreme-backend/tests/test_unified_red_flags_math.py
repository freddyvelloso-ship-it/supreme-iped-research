from __future__ import annotations

from datetime import date

from src.engine.supreme.models import IEORecord
from src.engine.supreme.red_flags import PSIWindow, evaluate_red_flags


def _ieo(window_start: date, *, z_t: float = 1.6, z_e: float = 0.5, z_v: float = 0.2, z_d: float = 0.1):
    return IEORecord(
        id_hash="subject-1",
        window_start=window_start,
        ieo_score=0.9,
        ieo_linear=1.0,
        ieo_sat=0.5,
        z_t=z_t,
        z_e=z_e,
        z_v=z_v,
        z_d=z_d,
    )


def test_reatividade_from_exposure_and_panas_increase():
    current = PSIWindow(
        id_hash="subject-1",
        window_start=date(2026, 2, 1),
        psi_score=1.0,
        z_panas_neg=1.2,
        z_dass=1.2,
        z_olbi=0.2,
        z_srq=0.2,
    )
    previous = PSIWindow(
        id_hash="subject-1",
        window_start=date(2026, 1, 18),
        psi_score=0.2,
        z_panas_neg=0.1,
    )

    flags = evaluate_red_flags(_ieo(current.window_start), current, [previous, current])

    assert [flag.flag_type for flag in flags] == ["reatividade"]
    assert flags[0].algorithm_version == "SUPREME-ANALYTICS-1.0.0"


def test_dissonancia_from_high_exposure_without_psychometric_elevation():
    current = PSIWindow(
        id_hash="subject-1",
        window_start=date(2026, 2, 1),
        psi_score=-0.2,
        z_panas_neg=0.0,
        z_dass=0.1,
        z_olbi=0.1,
        z_srq=0.1,
    )

    flags = evaluate_red_flags(_ieo(current.window_start), current, [current])

    assert [flag.flag_type for flag in flags] == ["dissonancia"]


def test_cronicidade_from_repeated_olbi_with_normal_exposure():
    previous = PSIWindow(
        id_hash="subject-1",
        window_start=date(2026, 1, 18),
        psi_score=1.1,
        z_olbi=1.2,
    )
    current = PSIWindow(
        id_hash="subject-1",
        window_start=date(2026, 2, 1),
        psi_score=1.3,
        z_olbi=1.4,
    )

    flags = evaluate_red_flags(
        _ieo(current.window_start, z_t=0.1, z_e=0.1, z_v=0.1, z_d=0.1),
        current,
        [previous, current],
    )

    assert [flag.flag_type for flag in flags] == ["cronicidade"]
