# Runbook - Redis Unavailable

Check Redis health, password configuration and RQ workers. After Redis recovers,
verify queue depth and run the local E2E if the incident touched ingestion.

