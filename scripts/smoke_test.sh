#!/usr/bin/env bash
set -euo pipefail
BASE=${BASE_URL:-https://localhost}
PROMETHEUS=${PROMETHEUS_URL:-http://localhost:9090}
TOKEN=${API_SECRET_KEY:?defina API_SECRET_KEY}
curl -kfsS "$BASE/" >/dev/null
curl -kfsS "$BASE/health" >/dev/null
curl -kfsS -H "Authorization: Bearer $TOKEN" "$BASE/v1/health" >/dev/null
curl -fsS "$PROMETHEUS/-/ready" >/dev/null
curl -fsS "$PROMETHEUS/api/v1/targets?state=active" | grep -q '"job":"supreme-api".*"health":"up"'
