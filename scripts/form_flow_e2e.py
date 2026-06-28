from __future__ import annotations

import argparse
import http.cookiejar
import json
import os
import ssl
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path


INSTRUMENTS = {
    "SRQ20": [0] * 20,
    "DASS21": [0] * 21,
    "OLBI": [1] * 16,
    "PANAS_SHORT": [1] * 10,
}


def read_env_value(path: Path, key: str) -> str | None:
    if not path.exists():
        return None
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith(f"{key}="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    return None


def request_json(opener, url: str, *, method: str = "GET", headers=None, data=None):
    body = None if data is None else json.dumps(data).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        headers=headers or {},
        method=method,
    )
    with opener.open(req, timeout=15) as response:
        raw = response.read().decode("utf-8")
        return json.loads(raw) if raw else {}


def assert_http_error(opener, url: str, expected_status: int, *, method="GET", headers=None, data=None):
    body = None if data is None else json.dumps(data).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers=headers or {}, method=method)
    try:
        opener.open(req, timeout=15).read()
    except urllib.error.HTTPError as exc:
        if exc.code != expected_status:
            raise AssertionError(f"expected HTTP {expected_status}, got {exc.code}") from exc
        return
    raise AssertionError(f"expected HTTP {expected_status}, got success")


def build_opener(insecure_tls: bool):
    cookie_jar = http.cookiejar.CookieJar()
    handlers = [urllib.request.HTTPCookieProcessor(cookie_jar)]
    if insecure_tls:
        handlers.append(urllib.request.HTTPSHandler(context=ssl._create_unverified_context()))
    return urllib.request.build_opener(*handlers)


def main() -> int:
    parser = argparse.ArgumentParser(description="SUPREME signed psychometric form E2E test")
    parser.add_argument("--base-url", default=os.getenv("BASE_URL", "https://localhost"))
    parser.add_argument("--api-secret-key", default=os.getenv("API_SECRET_KEY"))
    parser.add_argument("--env-file", default="supreme-backend/.env.production")
    parser.add_argument("--insecure-tls", action="store_true", default=True)
    args = parser.parse_args()

    api_secret = args.api_secret_key or read_env_value(Path(args.env_file), "API_SECRET_KEY")
    if not api_secret:
        raise SystemExit("API_SECRET_KEY ausente. Defina env var ou informe --env-file.")

    base = args.base_url.rstrip("/")
    admin_headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_secret}"}
    plain_headers = {"Content-Type": "application/json"}

    assert_http_error(
        build_opener(args.insecure_tls),
        f"{base}/v1/psychometric/submit",
        401,
        method="POST",
        headers=plain_headers,
        data={"id_hash": "phase3-no-session", "instrument": "SRQ20", "responses": [0] * 20},
    )

    results = []
    run_id = int(time.time())
    for instrument, responses in INSTRUMENTS.items():
        opener = build_opener(args.insecure_tls)
        id_hash = f"phase3-e2e-{instrument.lower()}-{run_id}"
        link = request_json(
            opener,
            f"{base}/v1/forms/link",
            method="POST",
            headers=admin_headers,
            data={"id_hash": id_hash, "instrument": instrument},
        )
        url = link["launch_url"]
        exposed_urls = [link.get("url", ""), url]
        if any("token=" in item or "API_INGEST_TOKEN" in item for item in exposed_urls):
            raise AssertionError(f"unsafe form URL for {instrument}: {exposed_urls}")
        opener.open(f"{base}{url}", timeout=15).read()
        session = request_json(opener, f"{base}/v1/forms/session")
        if session["id_hash"] != id_hash or session["instrument"] != instrument:
            raise AssertionError(f"invalid session for {instrument}: {session}")
        submit = request_json(
            opener,
            f"{base}/v1/psychometric/submit",
            method="POST",
            headers=plain_headers,
            data={"id_hash": id_hash, "instrument": instrument, "responses": responses},
        )
        if submit.get("status") != "ok":
            raise AssertionError(f"submit failed for {instrument}: {submit}")
        results.append({"instrument": instrument, "record_id": submit.get("record_id")})

    print(json.dumps({"status": "ok", "validated": results}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
