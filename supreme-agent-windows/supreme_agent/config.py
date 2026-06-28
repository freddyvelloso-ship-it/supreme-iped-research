from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AgentConfig:
    agent_id: str
    institution_id: str
    study_id: str
    case_id: str
    participant_scope: str
    server_url: str
    ingest_token: str
    queue_dir: Path
    plugin_event_log: Path
    signing_key: bytes
    encryption_key: bytes

    @property
    def queue_file(self) -> Path:
        return self.queue_dir / "outbox.ndjson"

    @property
    def chain_file(self) -> Path:
        return self.queue_dir / "chain.head"
