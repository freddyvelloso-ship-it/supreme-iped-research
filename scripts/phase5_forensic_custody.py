from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SUPREME_BACKEND = ROOT / "supreme-backend"
if str(SUPREME_BACKEND) not in sys.path:
    sys.path.insert(0, str(SUPREME_BACKEND))

from src.engine.supreme.algorithm import CURRENT_ALGORITHM_VERSION
from src.engine.supreme.forensic import (
    build_forensic_export,
    build_hash_chain,
    build_integrity_report,
    build_manifest,
    canonical_json,
    chain_tip,
    replay_pipeline,
    sha256_hex,
    sign_event,
    verify_forensic_export,
)
from src.engine.supreme.models import EventRecord


OUTPUT_DIR = ROOT / "docs" / "phase5_forensic"
SIGNED_EVENTS_PATH = OUTPUT_DIR / "signed_events.jsonl"
INPUT_CHAIN_PATH = OUTPUT_DIR / "input_hash_chain.json"
PROCESSING_CHAIN_PATH = OUTPUT_DIR / "processing_hash_chain.json"
OUTPUT_CHAIN_PATH = OUTPUT_DIR / "output_hash_chain.json"
ADMIN_AUDIT_PATH = OUTPUT_DIR / "admin_audit_log.jsonl"
MANIFEST_PATH = OUTPUT_DIR / "session_manifest.json"
INTEGRITY_REPORT_PATH = OUTPUT_DIR / "integrity_report.json"
FORENSIC_EXPORT_PATH = OUTPUT_DIR / "forensic_export.json"
DOC_PATH = ROOT / "docs" / "PHASE_FIVE_FORENSIC_CUSTODY.md"

SESSION_ID = "phase5-simulated-iped-session-001"
KEY_ID = "phase5-demo-custody-key-v1"
DEMO_SIGNING_MATERIAL = "phase5-demo-forensic-material-v1"


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n", encoding="utf-8")


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(row, sort_keys=True, ensure_ascii=True) + "\n" for row in rows),
        encoding="utf-8",
    )


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def build_simulated_iped_events() -> list[EventRecord]:
    base = [
        ("2026-01-01T08:00:00+00:00", "image_view", "image", 2, 12.0),
        ("2026-01-01T08:07:00+00:00", "video_play", "video", 2, 55.0),
        ("2026-01-15T08:00:00+00:00", "image_view", "image", 3, 15.0),
        ("2026-01-15T08:09:00+00:00", "video_play", "video", 3, 70.0),
        ("2026-01-29T08:00:00+00:00", "image_view", "image", 4, 20.0),
        ("2026-01-29T08:11:00+00:00", "video_play", "video", 4, 85.0),
        ("2026-02-12T08:00:00+00:00", "image_view", "image", 5, 25.0),
        ("2026-02-12T08:13:00+00:00", "video_play", "video", 5, 100.0),
    ]
    return [
        EventRecord(
            timestamp=datetime.fromisoformat(ts),
            event_type=event_type,
            media_type=media_type,
            severity=severity,
            duration_seconds=duration,
            user_identifier=sha256_hex("phase5-simulated-participant-001"),
            source_tool="iped",
        )
        for ts, event_type, media_type, severity, duration in base
    ]


def admin_audit_records() -> list[dict[str, Any]]:
    return [
        {
            "audit_type": "admin_change",
            "action": "role_scope_reviewed",
            "actor_id_hash": sha256_hex("phase5-admin-actor-001"),
            "target_scope": {"institution": "synthetic-institution", "study": "phase5-custody"},
            "before": {"role": "operador"},
            "after": {"role": "auditor"},
            "timestamp": "2026-06-23T00:00:00+00:00",
            "reason": "forensic custody verification fixture",
        },
        {
            "audit_type": "admin_change",
            "action": "algorithm_version_attested",
            "actor_id_hash": sha256_hex("phase5-admin-actor-002"),
            "target_scope": {"algorithm_version": CURRENT_ALGORITHM_VERSION},
            "before": {"attested": False},
            "after": {"attested": True},
            "timestamp": "2026-06-23T00:01:00+00:00",
            "reason": "algorithm evidence registry for deterministic replay",
        },
    ]


def version_registry() -> dict[str, str]:
    return {
        "iped": "simulated-iped-fixture-1.0.0",
        "iped_patch": "supreme-iped-audit-patch-1.0.0",
        "proxy": "supreme-iped-proxy-1.0.0",
        "watcher": "supreme-watch-iped-audit-tail-1.0.0",
        "supreme": "SUPREME-V4",
        "sentinela": "SENTINELA-PRODUCT-V1",
        "algorithm": CURRENT_ALGORITHM_VERSION,
    }


def build_artifacts() -> dict[str, Any]:
    events = build_simulated_iped_events()
    signed_events = [
        sign_event(event, DEMO_SIGNING_MATERIAL, key_id=KEY_ID, signed_at="2026-06-23T00:00:00+00:00")
        for event in events
    ]
    replay = replay_pipeline(events)
    input_chain = build_hash_chain(signed_events, chain_id="phase5-input")
    processing_chain = build_hash_chain(replay["processing"], chain_id="phase5-processing")
    output_chain = build_hash_chain(replay["outputs"], chain_id="phase5-output")
    admin_chain = build_hash_chain(admin_audit_records(), chain_id="phase5-admin-audit")
    manifest = build_manifest(
        session_id=SESSION_ID,
        evidence_mode="simulated_iped",
        versions=version_registry(),
        input_chain=input_chain,
        processing_chain=processing_chain,
        output_chain=output_chain,
        admin_audit_chain=admin_chain,
        real_iped_available=False,
    )
    integrity = build_integrity_report(
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
        integrity_report=integrity,
    )
    return {
        "signed_events": signed_events,
        "input_chain": input_chain,
        "processing_chain": processing_chain,
        "output_chain": output_chain,
        "admin_chain": admin_chain,
        "manifest": manifest,
        "integrity": integrity,
        "export": export,
        "replay": replay,
    }


def write_artifacts(artifacts: dict[str, Any]) -> None:
    _write_jsonl(SIGNED_EVENTS_PATH, artifacts["signed_events"])
    _write_json(INPUT_CHAIN_PATH, artifacts["input_chain"])
    _write_json(PROCESSING_CHAIN_PATH, artifacts["processing_chain"])
    _write_json(OUTPUT_CHAIN_PATH, artifacts["output_chain"])
    _write_jsonl(ADMIN_AUDIT_PATH, [entry["record"] for entry in artifacts["admin_chain"]])
    _write_json(MANIFEST_PATH, artifacts["manifest"])
    _write_json(INTEGRITY_REPORT_PATH, artifacts["integrity"])
    _write_json(FORENSIC_EXPORT_PATH, artifacts["export"])
    DOC_PATH.write_text(render_documentation(artifacts), encoding="utf-8")


def render_documentation(artifacts: dict[str, Any]) -> str:
    manifest = artifacts["manifest"]
    report = artifacts["integrity"]
    return "\n".join([
        "# SUPREME V4 - Phase 5 Forensic Custody",
        "",
        "Status: deterministic forensic custody package generated and verified for a simulated IPED event flow.",
        "",
        "## Scope",
        "",
        "This phase implements verifiable custody for synthetic/simulated IPED evidence and provides the same",
        "manifest structure for real IPED sessions when an authorized real environment is available. No real IPED",
        "case data is included in these artifacts.",
        "",
        "Evidence types:",
        "",
        "- Local simulated evidence: executed by `scripts/phase5_forensic_custody.py`.",
        "- Real IPED evidence: supported by the manifest fields and real-environment acceptance scripts, but not",
        "  executed in this Codex environment because no authorized real IPED session was provided.",
        "",
        "## Custody Controls",
        "",
        "- Events are signed at the first trusted SUPREME capture point.",
        "- Input, processing, output and administrative audit records are protected by hash chains.",
        "- Session manifest records IPED, patch, proxy, watcher, SUPREME, SENTINELA and algorithm versions.",
        "- Deterministic replay reconstructs analytical outputs from signed event payloads.",
        "- The verifier fails on signature, hash, manifest, version or replay divergence.",
        "",
        "## Current Manifest",
        "",
        f"- Session ID: `{manifest['session_id']}`",
        f"- Evidence mode: `{manifest['evidence_mode']}`",
        f"- Input chain tip: `{manifest['input_chain_tip']}`",
        f"- Processing chain tip: `{manifest['processing_chain_tip']}`",
        f"- Output chain tip: `{manifest['output_chain_tip']}`",
        f"- Admin audit chain tip: `{manifest['admin_audit_chain_tip']}`",
        f"- Manifest hash: `{manifest['manifest_hash']}`",
        "",
        "## Integrity Report",
        "",
        f"- Signed events: `{report['signed_event_count']}`",
        f"- Outputs: `{report['output_count']}`",
        f"- Replay digest: `{report['replay_digest']}`",
        f"- Algorithm version: `{manifest['versions']['algorithm']}`",
        "",
        "## Verification Commands",
        "",
        "```powershell",
        "python scripts\\phase5_forensic_custody.py check",
        "powershell -NoProfile -ExecutionPolicy Bypass -File scripts\\phase5_forensic_custody_check.ps1 -Root .",
        "```",
        "",
        "## Limits",
        "",
        "- These artifacts do not include real case data.",
        "- Real IPED sessions require authorized local execution of the IPED environment acceptance scripts.",
        "- Custody verification proves integrity and replayability of the captured data path; it does not prove",
        "  clinical diagnosis or causal attribution.",
        "",
    ])


def check_outputs() -> dict[str, Any]:
    required = [
        SIGNED_EVENTS_PATH,
        INPUT_CHAIN_PATH,
        PROCESSING_CHAIN_PATH,
        OUTPUT_CHAIN_PATH,
        ADMIN_AUDIT_PATH,
        MANIFEST_PATH,
        INTEGRITY_REPORT_PATH,
        FORENSIC_EXPORT_PATH,
        DOC_PATH,
    ]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.exists()]
    if missing:
        raise SystemExit(f"Missing Phase 5 forensic artifacts: {missing}")

    export = _read_json(FORENSIC_EXPORT_PATH)
    verify_forensic_export(export, DEMO_SIGNING_MATERIAL)

    fresh = build_artifacts()["export"]
    stored_canonical = canonical_json(export)
    fresh_canonical = canonical_json(fresh)
    if stored_canonical != fresh_canonical:
        raise SystemExit("Stored Phase 5 forensic export differs from deterministic regeneration.")

    signed_events = _read_jsonl(SIGNED_EVENTS_PATH)
    if len(signed_events) != export["integrity_report"]["signed_event_count"]:
        raise SystemExit("Signed JSONL count differs from integrity report.")
    return {
        "status": "ok",
        "manifest_hash": export["manifest"]["manifest_hash"],
        "export_hash": export["export_hash"],
        "input_chain_tip": chain_tip(export["chains"]["input"]),
        "output_chain_tip": chain_tip(export["chains"]["output"]),
        "signed_event_count": len(signed_events),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="SUPREME V4 Phase 5 forensic custody")
    parser.add_argument("action", choices=["all", "generate", "check"])
    args = parser.parse_args()

    if args.action in {"all", "generate"}:
        artifacts = build_artifacts()
        write_artifacts(artifacts)
        result = check_outputs()
        print(json.dumps(result, sort_keys=True))
        return 0
    if args.action == "check":
        result = check_outputs()
        print(json.dumps(result, sort_keys=True))
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
