from __future__ import annotations

from datetime import date, datetime, timezone
from math import log1p

from src.engine.supreme.algorithm import CURRENT_ALGORITHM_VERSION, algorithm_parameters
from src.engine.supreme.ieo import compute_ieo, ieo_final, ieo_linear, ieo_saturation
from src.engine.supreme.metrics import compute_window_metrics
from src.engine.supreme.models import (
    BaselineParameters,
    EventRecord,
    EventType,
    MediaType,
    SessionRecord,
    SourceTool,
    WindowMetrics,
    ZScores,
    event_weight,
)


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


def test_canonical_alfa_beta_severity_ratio_is_five_to_one():
    assert event_weight(MediaType.IMAGE, 1) == 1.0
    assert event_weight(MediaType.IMAGE, 3) == 1.0
    assert event_weight(MediaType.IMAGE, 4) == 5.0
    assert event_weight(MediaType.IMAGE, 5) / event_weight(MediaType.IMAGE, 1) == 5.0


def test_weighted_volume_preserves_event_duration_and_uses_canonical_log():
    events = [
        EventRecord(
            timestamp=datetime(2026, 1, 15, 10, 0, tzinfo=timezone.utc),
            event_type=EventType.IMAGE_VIEW,
            media_type=MediaType.IMAGE,
            severity=1,
            duration_seconds=60.0,
            user_identifier="a" * 64,
            source_tool=SourceTool.IPED,
        ),
        EventRecord(
            timestamp=datetime(2026, 1, 15, 10, 5, tzinfo=timezone.utc),
            event_type=EventType.IMAGE_VIEW,
            media_type=MediaType.IMAGE,
            severity=5,
            duration_seconds=120.0,
            user_identifier="a" * 64,
            source_tool=SourceTool.IPED,
        ),
    ]
    sessions = [
        SessionRecord(
            session_id="session-1",
            id_hash="a" * 64,
            session_start=datetime(2026, 1, 15, 10, 0, tzinfo=timezone.utc),
            session_end=datetime(2026, 1, 15, 10, 10, tzinfo=timezone.utc),
            duration_minutes=10.0,
            event_count=2,
        )
    ]

    metrics = compute_window_metrics(
        "a" * 64,
        date(2026, 1, 15),
        events,
        sessions,
    )

    assert metrics.v_volume == round(log1p(11.0), 4)


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
