from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
AGENT = ROOT / "supreme-agent-windows"
sys.path.insert(0, str(AGENT))

from supreme_agent.config import AgentConfig  # noqa: E402
from supreme_agent.crypto import decrypt_json, sha256_hex, verify  # noqa: E402
from supreme_agent.mapper import event_to_supreme_record  # noqa: E402
from supreme_agent.queue import enqueue, read_records  # noqa: E402


def build_config(root: Path) -> AgentConfig:
    queue_dir = root / "reports" / "phase8" / "agent-queue"
    plugin_log = root / "reports" / "phase8" / "sample-plugin-events.ndjson"
    return AgentConfig(
        agent_id="phase8-agent-simulated",
        institution_id="phase8-institution",
        study_id="phase8-study",
        case_id="phase8-case",
        participant_scope="phase8-operator",
        server_url="https://sentinela.example.invalid",
        ingest_token="not-used-in-replay",
        queue_dir=queue_dir,
        plugin_event_log=plugin_log,
        signing_key=b"phase8-signing-key-local-only-0000000000",
        encryption_key=b"phase8-encryption-key-local-only-00000000",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=str(ROOT))
    args = parser.parse_args()
    root = Path(args.root).resolve()
    config = build_config(root)
    config.queue_dir.mkdir(parents=True, exist_ok=True)
    if config.queue_file.exists():
        config.queue_file.unlink()
    if config.chain_file.exists():
        config.chain_file.unlink()

    events = [
        {
            "schema_version": "SUPREME-FIELD-EVENTS-1.0",
            "plugin_version": "SUPREME-IPED-PLUGIN-1.0.0",
            "agent_version": "SUPREME-AGENT-WINDOWS-1.0.0",
            "iped_version": "4.4.0-SNAPSHOT",
            "event_type": "image_view",
            "timestamp": "2026-06-23T12:00:00Z",
            "media_type": "image",
            "severity": "3",
            "duration_seconds": "2.500",
            "item_id": "101",
            "source_id": "1",
            "item_hash": sha256_hex("sample-item"),
        },
        {
            "schema_version": "SUPREME-FIELD-EVENTS-1.0",
            "plugin_version": "SUPREME-IPED-PLUGIN-1.0.0",
            "agent_version": "SUPREME-AGENT-WINDOWS-1.0.0",
            "iped_version": "4.4.0-SNAPSHOT",
            "event_type": "item_close",
            "timestamp": "2026-06-23T12:00:03Z",
            "media_type": "image",
            "severity": "3",
            "duration_seconds": "3.000",
            "item_id": "101",
            "source_id": "1",
            "item_hash": sha256_hex("sample-item"),
        },
    ]
    for event in events:
        enqueue(config, event)

    records = read_records(config)
    outputs = []
    previous = ""
    for record in records:
        envelope = decrypt_json(record["encrypted_envelope"], config.encryption_key)
        signature = envelope.pop("signature")
        if not verify(envelope, signature, config.signing_key):
            raise SystemExit("invalid signature")
        if envelope["previous_hash"] != previous:
            raise SystemExit("chain order mismatch")
        previous = envelope["chain_hash"]
        envelope["signature"] = signature
        outputs.append(event_to_supreme_record(envelope))

    report = {
        "status": "ok",
        "records": len(records),
        "outputs": len(outputs),
        "final_chain_hash": previous,
        "output_hash": sha256_hex(json.dumps(outputs, sort_keys=True)),
    }
    report_path = root / "reports" / "phase8" / "field_replay_report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
