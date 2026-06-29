from __future__ import annotations

import argparse
import hashlib
import json
import os
import ssl
import subprocess
import sys
import time
import urllib.request
from pathlib import Path


def read_env_value(path: Path, key: str) -> str | None:
    if not path.exists():
        return None
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith(f"{key}="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    return None


def request_json(url: str, *, method: str, token: str, data: dict):
    ctx = ssl._create_unverified_context()
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode("utf-8"),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"},
        method=method,
    )
    with urllib.request.urlopen(req, context=ctx, timeout=15) as response:
        raw = response.read().decode("utf-8")
        return json.loads(raw) if raw else {}


def compose_exec(service: str, *args: str) -> str:
    project_name = os.getenv("COMPOSE_PROJECT_NAME", "supreme-v4-test-clone")
    cmd = [
        "docker",
        "compose",
        "-p",
        project_name,
        "-f",
        "docker-compose.production.yml",
        "-f",
        "docker-compose.local.yml",
        "exec",
        "-T",
        service,
        *args,
    ]
    result = subprocess.run(cmd, check=False, text=True, capture_output=True)
    if result.returncode != 0:
        detail = (result.stderr or result.stdout or "").strip()
        raise RuntimeError(f"docker compose exec {service} failed: {detail[:500]}")
    return result.stdout.strip()


def sql_literal(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def pseudonymize(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def psql(service: str, user: str, db: str, sql: str) -> str:
    return compose_exec(service, "psql", "-U", user, "-d", db, "-tAc", sql)


def wait_for(predicate, timeout_seconds: int, label: str):
    deadline = time.time() + timeout_seconds
    last = None
    while time.time() < deadline:
        last = predicate()
        if last:
            return last
        time.sleep(2)
    raise AssertionError(f"timeout aguardando {label}; ultimo={last!r}")


def event(timestamp: str, event_type: str, media_type: str, severity: int, duration: float, user: str) -> dict:
    return {
        "timestamp": timestamp,
        "event_type": event_type,
        "media_type": media_type,
        "severity": severity,
        "duration_seconds": duration,
        "user_identifier": user,
        "source_tool": "iped",
    }


def build_operational_payload(id_hash: str) -> dict:
    # Four completed 14-day windows are required before the analytics engine can
    # build a baseline, compute IEO and push an auditable window to SENTINELA.
    rows = [
        ("2026-01-03T10:00:00+00:00", "image_view", "image", 2, 60.0),
        ("2026-01-03T10:06:00+00:00", "video_play", "video", 3, 120.0),
        ("2026-01-17T10:00:00+00:00", "image_view", "image", 3, 75.0),
        ("2026-01-17T10:08:00+00:00", "classification_event", "preview", 2, 20.0),
        ("2026-01-31T10:00:00+00:00", "image_view", "image", 4, 80.0),
        ("2026-01-31T10:08:00+00:00", "video_play", "video", 4, 160.0),
        ("2026-02-14T10:00:00+00:00", "image_view", "image", 5, 90.0),
        ("2026-02-14T10:09:00+00:00", "video_play", "video", 5, 180.0),
    ]
    return {"events": [event(*row, user=id_hash) for row in rows]}


def main() -> int:
    parser = argparse.ArgumentParser(description="SUPREME IPED-like operational E2E")
    parser.add_argument("--base-url", default=os.getenv("BASE_URL", "https://localhost"))
    parser.add_argument("--api-secret-key", default=os.getenv("API_SECRET_KEY"))
    parser.add_argument("--api-ingest-token", default=os.getenv("API_INGEST_TOKEN"))
    parser.add_argument("--env-file", default="supreme-backend/.env.production")
    parser.add_argument("--root-env-file", default=".env")
    parser.add_argument("--require-sentinela", action="store_true")
    parser.add_argument("--timeout-seconds", type=int, default=90)
    args = parser.parse_args()

    api_secret = args.api_secret_key or read_env_value(Path(args.env_file), "API_SECRET_KEY")
    ingest_token = args.api_ingest_token or read_env_value(Path(args.env_file), "API_INGEST_TOKEN")
    if not ingest_token:
        ingest_token = read_env_value(Path(args.root_env_file), "API_INGEST_TOKEN")
    if not api_secret or not ingest_token:
        raise SystemExit("API_SECRET_KEY/API_INGEST_TOKEN ausentes.")

    base = args.base_url.rstrip("/")
    run_id = int(time.time())
    id_hash = pseudonymize(f"phase4-iped-e2e-{run_id}")
    request_json(
        f"{base}/v1/governance/consent/{id_hash}",
        method="POST",
        token=api_secret,
        data={"status": "granted"},
    )

    ingest = request_json(
        f"{base}/v1/events/ingest",
        method="POST",
        token=ingest_token,
        data=build_operational_payload(id_hash),
    )
    if ingest.get("events_stored", 0) < 8:
        raise AssertionError(f"ingest nao armazenou eventos: {ingest}")

    id_sql = sql_literal(id_hash)

    events_count = wait_for(
        lambda: int(psql("supreme-db", "supreme", "supreme", f"SELECT COUNT(*) FROM events_raw WHERE id_hash={id_sql};") or "0"),
        args.timeout_seconds,
        "events_raw",
    )

    pipeline_status = wait_for(
        lambda: psql(
            "supreme-db",
            "supreme",
            "supreme",
            "SELECT status FROM system_health_logs "
            f"WHERE id_hash={id_sql} AND pipeline_stage='pipeline' "
            "ORDER BY timestamp DESC LIMIT 1;",
        ),
        args.timeout_seconds,
        "system_health_logs pipeline",
    )

    metrics_count = int(
        psql("supreme-db", "supreme", "supreme", f"SELECT COUNT(*) FROM window_metrics WHERE id_hash={id_sql};")
        or "0"
    )

    sentinela_count = None
    if args.require_sentinela:
        sentinela_count = wait_for(
            lambda: int(
                psql("sentinela-db", "sentinela", "sentinela", f"SELECT COUNT(*) FROM ieo_windows WHERE id_hash={id_sql};")
                or "0"
            ),
            args.timeout_seconds,
            "sentinela ieo_windows",
        )

    print(
        json.dumps(
            {
                "status": "ok",
                "id_hash": id_hash,
                "events_raw": events_count,
                "window_metrics": metrics_count,
                "pipeline_status": pipeline_status,
                "sentinela_ieo_windows": sentinela_count,
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
