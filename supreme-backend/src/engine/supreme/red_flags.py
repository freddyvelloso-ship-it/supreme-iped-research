"""SUPREME-owned red-flag engine.

SENTINELA must only visualize these outputs. It must not recompute critical
classification rules from dashboard data.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any, Optional

from .algorithm import ALGORITHM_SPEC, CURRENT_ALGORITHM_VERSION
from .models import IEORecord


@dataclass(frozen=True)
class PSIWindow:
    id_hash: str
    window_start: date
    psi_score: Optional[float] = None
    z_dass: Optional[float] = None
    z_olbi: Optional[float] = None
    z_srq: Optional[float] = None
    z_panas_neg: Optional[float] = None
    convergence_class: Optional[str] = None


@dataclass(frozen=True)
class AnalyticRedFlag:
    id_hash: str
    window_start: date
    flag_type: str
    severity: str
    detail: dict[str, Any]
    algorithm_version: str = CURRENT_ALGORITHM_VERSION


def exposure_z(ieo: IEORecord) -> float:
    """A conservative scalar exposure signal derived from individual IEO z-scores."""
    return max(ieo.z_t, ieo.z_e, ieo.z_v, ieo.z_d)


def check_reatividade(
    exposure_z_value: Optional[float],
    panas_na_current: Optional[float],
    panas_na_prev: Optional[float],
) -> Optional[str]:
    params = ALGORITHM_SPEC.red_flags
    if exposure_z_value is None or exposure_z_value < params.exposure_z_threshold:
        return None
    if panas_na_current is None:
        return None
    na_high_without_history = panas_na_prev is None and panas_na_current >= params.psychometric_high_z_threshold
    na_increased = panas_na_prev is not None and panas_na_current > panas_na_prev
    if na_high_without_history or na_increased:
        return "maior" if exposure_z_value >= params.major_exposure_z_threshold else "moderado"
    return None


def check_dissonancia(
    exposure_z_value: Optional[float],
    dass_stable: bool,
    olbi_stable: bool,
    srq_stable: bool,
) -> Optional[str]:
    params = ALGORITHM_SPEC.red_flags
    if exposure_z_value is None or exposure_z_value < params.exposure_z_threshold:
        return None
    if dass_stable and olbi_stable and srq_stable:
        return "maior" if exposure_z_value >= params.major_exposure_z_threshold else "moderado"
    return None


def check_cronicidade(
    exposure_z_value: Optional[float],
    olbi_high_streak: int,
    srq_high_streak: int,
) -> Optional[str]:
    params = ALGORITHM_SPEC.red_flags
    if exposure_z_value is not None and abs(exposure_z_value) >= params.exposure_z_threshold:
        return None
    streak = max(olbi_high_streak, srq_high_streak)
    if streak >= params.chronic_windows:
        return "maior" if streak >= params.chronic_windows + 1 else "moderado"
    return None


def evaluate_red_flags(
    ieo: IEORecord,
    current_psi: Optional[PSIWindow],
    psi_history: list[PSIWindow],
) -> list[AnalyticRedFlag]:
    """Evaluate all typed red flags using only SUPREME analytical outputs."""
    if current_psi is None:
        return []

    params = ALGORITHM_SPEC.red_flags
    ez = exposure_z(ieo)
    previous = [
        row for row in sorted(psi_history, key=lambda p: p.window_start)
        if row.window_start < current_psi.window_start
    ]
    prev = previous[-1] if previous else None
    z_panas_prev = prev.z_panas_neg if prev else None

    z_dass = current_psi.z_dass
    z_olbi = current_psi.z_olbi
    z_srq = current_psi.z_srq
    z_panas = current_psi.z_panas_neg

    def stable(value: Optional[float]) -> bool:
        return value is None or value < params.psychometric_high_z_threshold

    olbi_streak = _high_streak([*previous, current_psi], "z_olbi")
    srq_streak = _high_streak([*previous, current_psi], "z_srq")

    flags: list[AnalyticRedFlag] = []

    severity = check_reatividade(ez, z_panas, z_panas_prev)
    if severity:
        flags.append(AnalyticRedFlag(
            id_hash=ieo.id_hash,
            window_start=ieo.window_start,
            flag_type="reatividade",
            severity=severity,
            detail={
                "exposure_z": round(ez, 6),
                "z_panas_neg": z_panas,
                "z_panas_neg_prev": z_panas_prev,
            },
        ))

    severity = check_dissonancia(ez, stable(z_dass), stable(z_olbi), stable(z_srq))
    if severity:
        flags.append(AnalyticRedFlag(
            id_hash=ieo.id_hash,
            window_start=ieo.window_start,
            flag_type="dissonancia",
            severity=severity,
            detail={
                "exposure_z": round(ez, 6),
                "z_dass": z_dass,
                "z_olbi": z_olbi,
                "z_srq": z_srq,
            },
        ))

    severity = check_cronicidade(ez, olbi_streak, srq_streak)
    if severity:
        flags.append(AnalyticRedFlag(
            id_hash=ieo.id_hash,
            window_start=ieo.window_start,
            flag_type="cronicidade",
            severity=severity,
            detail={
                "exposure_z": round(ez, 6),
                "olbi_high_streak": olbi_streak,
                "srq_high_streak": srq_streak,
            },
        ))

    return flags


def _high_streak(history: list[PSIWindow], attr: str) -> int:
    threshold = ALGORITHM_SPEC.red_flags.psychometric_high_z_threshold
    streak = 0
    for row in reversed(sorted(history, key=lambda p: p.window_start)):
        value = getattr(row, attr)
        if value is not None and value >= threshold:
            streak += 1
        else:
            break
    return streak
