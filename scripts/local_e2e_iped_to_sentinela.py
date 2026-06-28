from __future__ import annotations

import argparse
import json
import os
import ssl
import subprocess
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


COMPOSE = [
    "docker",
    "compose",
    "-p",
    os.getenv("COMPOSE_PROJECT_NAME", "supreme-v4-test-clone"),
    "-f",
    "docker-compose.production.yml",
    "-f",
    "docker-compose.local.yml",
]


def read_env_value(path: Path, key: str) -> str | None:
    if not path.exists():
        return None
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith(f"{key}="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    return None


def request_json(url: str, *, method: str, token: str, data: dict) -> dict:
    context = ssl._create_unverified_context()
    request = urllib.request.Request(
        url,
        data=json.dumps(data).encode("utf-8"),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"},
        method=method,
    )
    with urllib.request.urlopen(request, context=context, timeout=20) as response:
        raw = response.read().decode("utf-8")
        return json.loads(raw) if raw else {}


def compose_exec(service: str, *args: str) -> str:
    result = subprocess.run(
        [*COMPOSE, "exec", "-T", service, *args],
        check=False,
        text=True,
        capture_output=True,
    )
    if result.returncode != 0:
        detail = (result.stderr or result.stdout or "").strip()
        raise RuntimeError(f"docker compose exec {service} failed: {detail[:500]}")
    return result.stdout.strip()


def psql(service: str, user: str, database: str, sql: str) -> str:
    return compose_exec(service, "psql", "-U", user, "-d", database, "-tAc", sql)


def redis_cli(password: str, *args: str) -> str:
    return compose_exec("supreme-redis", "redis-cli", "--no-auth-warning", "-a", password, "--raw", *args)


def sql_literal(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def wait_for(label: str, timeout_seconds: int, predicate):
    deadline = time.time() + timeout_seconds
    last = None
    while time.time() < deadline:
        try:
            last = predicate()
            if last:
                return last
        except Exception as exc:  # noqa: BLE001 - surfaced below with context
            last = str(exc)
        time.sleep(3)
    raise AssertionError(f"timeout waiting for {label}; last={last!r}")


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


def build_payload(id_hash: str) -> dict:
    # Four completed 14-day windows are required to produce baseline and IEO.
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
    parser = argparse.ArgumentParser(description="Local E2E: simulated IPED event -> SUPREME -> Redis/RQ -> Postgres -> SENTINELA")
    parser.add_argument("--base-url", default=os.getenv("BASE_URL", "https://localhost"))
    parser.add_argument("--timeout-seconds", type=int, default=180)
    args = parser.parse_args()

    api_secret = read_env_value(Path("supreme-backend/.env.production"), "API_SECRET_KEY")
    ingest_token = read_env_value(Path("supreme-backend/.env.production"), "API_INGEST_TOKEN")
    redis_password = read_env_value(Path(".env"), "REDIS_PASSWORD")
    if not api_secret or not ingest_token or not redis_password:
        raise SystemExit("Missing API_SECRET_KEY, API_INGEST_TOKEN or REDIS_PASSWORD. Run scripts/setup_env_local.ps1.")

    base = args.base_url.rstrip("/")
    run_id = int(time.time())
    id_hash = f"phase1-e2e-{run_id}"
    id_sql = sql_literal(id_hash)

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
        data=build_payload(id_hash),
    )
    if ingest.get("events_stored", 0) < 8:
        raise AssertionError(f"expected at least 8 stored events; got {ingest}")

    events_raw = wait_for(
        "SUPREME events_raw",
        args.timeout_seconds,
        lambda: int(psql("supreme-db", "supreme", "supreme", f"SELECT COUNT(*) FROM events_raw WHERE id_hash={id_sql};") or "0"),
    )

    pipeline_status = wait_for(
        "SUPREME pipeline health log",
        args.timeout_seconds,
        lambda: psql(
            "supreme-db",
            "supreme",
            "supreme",
            "SELECT status FROM system_health_logs "
            f"WHERE id_hash={id_sql} AND pipeline_stage='pipeline' "
            "ORDER BY timestamp DESC LIMIT 1;",
        ),
    )

    window_metrics = wait_for(
        "SUPREME window_metrics",
        args.timeout_seconds,
        lambda: int(psql("supreme-db", "supreme", "supreme", f"SELECT COUNT(*) FROM window_metrics WHERE id_hash={id_sql};") or "0") >= 4,
    )

    ieo_logs = wait_for(
        "SUPREME ieo_logs",
        args.timeout_seconds,
        lambda: int(psql("supreme-db", "supreme", "supreme", f"SELECT COUNT(*) FROM ieo_logs WHERE id_hash={id_sql};") or "0"),
    )

    sentinela_windows = wait_for(
        "SENTINELA ieo_windows",
        args.timeout_seconds,
        lambda: int(psql("sentinela-db", "sentinela", "sentinela", f"SELECT COUNT(*) FROM ieo_windows WHERE id_hash={id_sql};") or "0"),
    )

    rq_keys = redis_cli(redis_password, "KEYS", "rq:*").splitlines()
    analytics_rq_observed = any(
        key in {"rq:queues", "rq:finished:analytics", "rq:workers:analytics"}
        or key.startswith("rq:worker:")
        for key in rq_keys
    )
    if not analytics_rq_observed:
        raise AssertionError(f"RQ analytics keys not observed in Redis: {rq_keys}")

    result = {
        "status": "ok",
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "id_hash": id_hash,
        "events_stored_http": ingest.get("events_stored"),
        "events_raw": events_raw,
        "redis_rq_analytics_observed": analytics_rq_observed,
        "pipeline_status": pipeline_status,
        "window_metrics_at_least_4": bool(window_metrics),
        "ieo_logs": ieo_logs,
        "sentinela_ieo_windows": sentinela_windows,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
