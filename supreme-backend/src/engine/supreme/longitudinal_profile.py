"""Operational longitudinal profile classifier for SUPREME V4.

The profile is a longitudinal operational classification for forensic work
monitoring. It is not a clinical diagnosis and does not infer causality.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone
from statistics import mean, pstdev
from typing import Any, Literal

from .algorithm import CURRENT_ALGORITHM_VERSION, ALGORITHM_SPEC, algorithm_parameters
from .models import BaselineParameters

ProfileClass = Literal["medio", "resiliente", "vulneravel", "junior", "senior"]

PROFILE_LABELS: dict[str, str] = {
    "medio": "Médio",
    "resiliente": "Resiliente",
    "vulneravel": "Vulnerável",
    "junior": "Júnior",
    "senior": "Sênior",
}


@dataclass(frozen=True)
class ProfileWindow:
    window_start: date
    ieo_score: float | None = None
    psi_score: float | None = None
    dq_score: float | None = None
    convergence_class: str | None = None


@dataclass(frozen=True)
class ProfileFlag:
    window_start: date
    flag_type: str
    severity: str


@dataclass(frozen=True)
class LongitudinalProfile:
    id_hash: str
    profile_class: ProfileClass
    profile_label: str
    profile_confidence: float
    profile_evidence: dict[str, Any]
    baseline_version: int | None
    algorithm_version: str
    algorithm_parameters: dict[str, Any]
    classified_at: datetime

    def to_record(self) -> dict[str, Any]:
        return {
            "id_hash": self.id_hash,
            "profile_class": self.profile_class,
            "profile_label": self.profile_label,
            "profile_confidence": self.profile_confidence,
            "profile_evidence": self.profile_evidence,
            "baseline_version": self.baseline_version,
            "algorithm_version": self.algorithm_version,
            "algorithm_parameters": self.algorithm_parameters,
            "classified_at": self.classified_at,
        }


def classify_longitudinal_profile(
    id_hash: str,
    baseline: BaselineParameters | None,
    windows: list[ProfileWindow],
    flags: list[ProfileFlag],
    classified_at: datetime | None = None,
) -> LongitudinalProfile:
    """Classify one expert profile from SUPREME outputs only.

    Deterministic rule order:
    insufficient/provisional -> vulnerable -> resilient -> junior -> senior -> medio.
    """
    params = ALGORITHM_SPEC.longitudinal_profile
    now = classified_at or datetime.now(timezone.utc)
    ordered = sorted(windows, key=lambda w: w.window_start)
    usable = [w for w in ordered if w.ieo_score is not None]
    ieo_values = [float(w.ieo_score) for w in usable if w.ieo_score is not None]
    psi_values = [float(w.psi_score) for w in ordered if w.psi_score is not None]
    dq_values = [float(w.dq_score) for w in ordered if w.dq_score is not None]
    flag_counts = _count_flags(flags)
    major_flag_count = sum(1 for f in flags if f.severity == "maior")
    chronicity_count = flag_counts.get("cronicidade", 0)
    dissonance_count = flag_counts.get("dissonancia", 0)

    evidence = {
        "classification_basis": "operational_longitudinal_profile",
        "non_diagnostic_notice": "operational_classification_requires_human_review",
        "n_windows": len(ordered),
        "n_ieo_windows": len(ieo_values),
        "n_psi_windows": len(psi_values),
        "avg_ieo": _round(mean(ieo_values)) if ieo_values else None,
        "latest_ieo": _round(ieo_values[-1]) if ieo_values else None,
        "ieo_slope": _round(ieo_values[-1] - ieo_values[0]) if len(ieo_values) >= 2 else None,
        "ieo_volatility": _round(pstdev(ieo_values)) if len(ieo_values) >= 2 else 0.0,
        "avg_psi": _round(mean(psi_values)) if psi_values else None,
        "latest_psi": _round(psi_values[-1]) if psi_values else None,
        "avg_dq": _round(mean(dq_values)) if dq_values else None,
        "flag_counts": flag_counts,
        "major_flag_count": major_flag_count,
        "baseline_frozen": bool(baseline and baseline.is_frozen()),
        "baseline_window_count": baseline.baseline_window_count if baseline else 0,
    }

    if not baseline or len(usable) < params.min_history_windows:
        evidence["provisional"] = True
        evidence["reason"] = "insufficient_baseline_or_history"
        return _profile(id_hash, "medio", params.provisional_confidence, evidence, baseline, now)

    avg_ieo = float(evidence["avg_ieo"] or 0.0)
    avg_psi = float(evidence["avg_psi"] or 0.0)
    latest_psi = float(evidence["latest_psi"] or 0.0)
    volatility = float(evidence["ieo_volatility"] or 0.0)
    slope = float(evidence["ieo_slope"] or 0.0)

    if (
        major_flag_count > 0
        or chronicity_count > 0
        or dissonance_count >= 2
        or latest_psi >= params.critical_psi_threshold
        or avg_psi >= params.elevated_psi_threshold
    ):
        evidence["reason"] = "elevated_psychometric_or_persistent_flags"
        return _profile(id_hash, "vulneravel", params.vulnerable_confidence, evidence, baseline, now)

    if avg_ieo >= params.high_ieo_threshold and avg_psi <= params.low_psi_threshold and not flags:
        evidence["reason"] = "high_exposure_with_low_psychometric_load"
        return _profile(id_hash, "resiliente", params.resilient_confidence, evidence, baseline, now)

    if (
        baseline.baseline_window_count <= params.junior_max_baseline_windows
        and volatility >= params.junior_volatility_threshold
        and avg_psi < params.elevated_psi_threshold
    ):
        evidence["reason"] = "early_baseline_with_high_operational_variability"
        return _profile(id_hash, "junior", params.junior_confidence, evidence, baseline, now)

    if (
        len(usable) >= params.senior_min_windows
        and avg_ieo <= params.senior_max_avg_ieo
        and avg_psi <= params.low_psi_threshold
        and abs(slope) <= params.senior_max_abs_slope
        and not flags
    ):
        evidence["reason"] = "stable_low_load_longitudinal_pattern"
        return _profile(id_hash, "senior", params.senior_confidence, evidence, baseline, now)

    evidence["reason"] = "no_extreme_longitudinal_pattern"
    return _profile(id_hash, "medio", params.medium_confidence, evidence, baseline, now)


def _profile(
    id_hash: str,
    profile_class: ProfileClass,
    confidence: float,
    evidence: dict[str, Any],
    baseline: BaselineParameters | None,
    classified_at: datetime,
) -> LongitudinalProfile:
    return LongitudinalProfile(
        id_hash=id_hash,
        profile_class=profile_class,
        profile_label=PROFILE_LABELS[profile_class],
        profile_confidence=_round(confidence),
        profile_evidence=evidence,
        baseline_version=baseline.baseline_version if baseline else None,
        algorithm_version=CURRENT_ALGORITHM_VERSION,
        algorithm_parameters=algorithm_parameters(),
        classified_at=classified_at,
    )


def _count_flags(flags: list[ProfileFlag]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for flag in flags:
        counts[flag.flag_type] = counts.get(flag.flag_type, 0) + 1
    return counts


def _round(value: float) -> float:
    return round(float(value), 4)
