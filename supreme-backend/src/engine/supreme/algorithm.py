"""Versioned analytical parameters for SUPREME V4.

This module is the single source of truth for analytical versions, weights and
thresholds used by IEO, PSI and red-flag classification.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


CURRENT_ALGORITHM_VERSION = "SUPREME-ANALYTICS-1.0.0"


@dataclass(frozen=True)
class IEOParameters:
    z_t: float = 0.5
    z_e: float = 0.3
    z_v: float = 0.2
    z_d_delta: float = 0.1
    logistic_k: float = 1.0
    logistic_x0: float = 1.0


@dataclass(frozen=True)
class PSIParameters:
    # Canonical hierarchy: proximity to acute exposure event.
    # PSI = 0.40 PANAS_neg + 0.30 DASS_total + 0.20 OLBI_exh + 0.10 SRQ.
    z_panas_neg: float = 0.40
    z_dass: float = 0.30
    z_olbi: float = 0.20
    z_srq: float = 0.10
    psi_threshold: float = 0.0
    oei_threshold: float = 0.0
    min_history_for_baseline: int = 4


@dataclass(frozen=True)
class RedFlagParameters:
    exposure_z_threshold: float = 1.5
    major_exposure_z_threshold: float = 2.0
    psychometric_high_z_threshold: float = 1.0
    chronic_windows: int = 2


@dataclass(frozen=True)
class LongitudinalProfileParameters:
    min_history_windows: int = 4
    provisional_confidence: float = 0.25
    medium_confidence: float = 0.60
    vulnerable_confidence: float = 0.84
    resilient_confidence: float = 0.78
    junior_confidence: float = 0.70
    senior_confidence: float = 0.76
    high_ieo_threshold: float = 0.65
    low_psi_threshold: float = 0.30
    elevated_psi_threshold: float = 0.80
    critical_psi_threshold: float = 1.00
    junior_max_baseline_windows: int = 4
    junior_volatility_threshold: float = 0.35
    senior_min_windows: int = 8
    senior_max_avg_ieo: float = 0.45
    senior_max_abs_slope: float = 0.15


@dataclass(frozen=True)
class AlgorithmSpec:
    version: str = CURRENT_ALGORITHM_VERSION
    ieo: IEOParameters = IEOParameters()
    psi: PSIParameters = PSIParameters()
    red_flags: RedFlagParameters = RedFlagParameters()
    longitudinal_profile: LongitudinalProfileParameters = LongitudinalProfileParameters()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


ALGORITHM_SPEC = AlgorithmSpec()


def algorithm_parameters() -> dict[str, Any]:
    """Return JSON-serializable parameters for audit storage."""
    return ALGORITHM_SPEC.to_dict()
