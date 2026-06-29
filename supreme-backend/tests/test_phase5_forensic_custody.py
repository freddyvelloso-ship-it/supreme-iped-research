from copy import deepcopy
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.engine.supreme.algorithm import CURRENT_ALGORITHM_VERSION  # noqa: E402
from src.engine.supreme.forensic import (  # noqa: E402
    build_forensic_export,
    build_hash_chain,
    build_integrity_report,
    build_manifest,
    replay_pipeline,
    sign_event,
    verify_forensic_export,
    verify_hash_chain,
    verify_signed_event,
)

SCRIPT_DIR = ROOT / "scripts"
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from phase5_forensic_custody import (  # noqa: E402
    DEMO_SIGNING_MATERIAL,
    KEY_ID,
    SESSION_ID,
    admin_audit_records,
    build_artifacts,
    build_simulated_iped_events,
    version_registry,
)


def test_event_signature_verifies_and_tamper_fails():
    event = build_simulated_iped_events()[0]
    signed = sign_event(event, DEMO_SIGNING_MATERIAL, key_id=KEY_ID)
    assert verify_signed_event(signed, DEMO_SIGNING_MATERIAL) is True

    tampered = deepcopy(signed)
    tampered["payload"]["severity"] = 5
    try:
        verify_signed_event(tampered, DEMO_SIGNING_MATERIAL)
    except ValueError as exc:
        assert "mismatch" in str(exc)
    else:
        raise AssertionError("tampered event signature should fail")


def test_hash_chain_verifies_and_tamper_fails():
    chain = build_hash_chain([{"a": 1}, {"b": 2}], chain_id="phase5-input")
    assert verify_hash_chain(chain, chain_id="phase5-input") is True

    tampered = deepcopy(chain)
    tampered[1]["record"]["b"] = 3
    try:
        verify_hash_chain(tampered, chain_id="phase5-input")
    except ValueError as exc:
        assert "mismatch" in str(exc)
    else:
        raise AssertionError("tampered chain should fail")


def test_manifest_contains_required_versions():
    artifacts = build_artifacts()
    versions = artifacts["manifest"]["versions"]
    for field in ["iped", "iped_patch", "proxy", "watcher", "supreme", "sentinela", "algorithm"]:
        assert versions[field]
    assert versions["algorithm"] == CURRENT_ALGORITHM_VERSION
    assert artifacts["manifest"]["evidence_mode"] == "simulated_iped"


def test_replay_is_deterministic_for_same_input():
    events = build_simulated_iped_events()
    first = replay_pipeline(events)
    second = replay_pipeline(events)
    assert first == second
    assert first["outputs"]
    assert all(output["algorithm_version"] == CURRENT_ALGORITHM_VERSION for output in first["outputs"])


def test_forensic_export_verifies_and_tamper_fails():
    artifacts = build_artifacts()
    assert verify_forensic_export(artifacts["export"], DEMO_SIGNING_MATERIAL) is True

    tampered = deepcopy(artifacts["export"])
    tampered["chains"]["output"][0]["record"]["ieo_score"] = 999
    try:
        verify_forensic_export(tampered, DEMO_SIGNING_MATERIAL)
    except ValueError as exc:
        assert "mismatch" in str(exc)
    else:
        raise AssertionError("tampered forensic export should fail")


def test_admin_audit_chain_and_integrity_report():
    events = build_simulated_iped_events()
    signed_events = [sign_event(event, DEMO_SIGNING_MATERIAL, key_id=KEY_ID) for event in events]
    replay = replay_pipeline(events)
    input_chain = build_hash_chain(signed_events, chain_id="phase5-input")
    processing_chain = build_hash_chain(replay["processing"], chain_id="phase5-processing")
    output_chain = build_hash_chain(replay["outputs"], chain_id="phase5-output")
    admin_chain = build_hash_chain(admin_audit_records(), chain_id="phase5-admin-audit")
    assert verify_hash_chain(admin_chain, chain_id="phase5-admin-audit") is True

    manifest = build_manifest(
        session_id=SESSION_ID,
        evidence_mode="simulated_iped",
        versions=version_registry(),
        input_chain=input_chain,
        processing_chain=processing_chain,
        output_chain=output_chain,
        admin_audit_chain=admin_chain,
    )
    report = build_integrity_report(
        manifest=manifest,
        signed_events=signed_events,
        input_chain=input_chain,
        processing_chain=processing_chain,
        output_chain=output_chain,
        admin_audit_chain=admin_chain,
        replay=replay,
    )
    export = build_forensic_export(
        manifest=manifest,
        signed_events=signed_events,
        input_chain=input_chain,
        processing_chain=processing_chain,
        output_chain=output_chain,
        admin_audit_chain=admin_chain,
        integrity_report=report,
    )
    assert report["status"] == "verifiable"
    assert report["signed_event_count"] == len(signed_events)
    assert verify_forensic_export(export, DEMO_SIGNING_MATERIAL) is True
