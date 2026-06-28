# Research Data Security And Sanitization

Status: hardened for doctoral research validation with real sanitized data.

This SUPREME-IPED package is designed to process analytic events, not raw forensic evidence. It must not ingest, persist, print, or transfer media, raw paths, names, emails, CPF/RG, phones, addresses, raw case identifiers, raw operator identifiers, raw item identifiers, raw hashes, raw CSV lines, psychometric item-level answers, diagnosis, rankings, productivity scoring, or disciplinary recommendations.

## Operational Contract

Allowed event-level data:

- `timestamp`
- `event_type`
- `media_type`
- `severity`
- `duration_seconds`
- `user_identifier` as a 64-character SHA-256 pseudonym only
- `source_tool`
- `event_hash` as a 64-character SHA-256 digest only

Anything outside this allowlist is rejected before backend ingestion.

## IPED Bridge

The IPED proxy and watcher now:

- derive `user_identifier` through salted SHA-256 pseudonymization;
- require a strong `SUPREME_SALT` with at least 32 characters;
- remove raw IPED item/source identifiers from SUPREME payloads;
- avoid logging raw audit lines, raw user identifiers, item IDs, paths, or file names;
- expose only whether the audit log is configured, not its filesystem path;
- fail closed when a payload contains unsafe fields.

## SUPREME Backend

The backend now:

- rejects raw or malformed `user_identifier`;
- rejects unexpected fields in event ingestion;
- validates `event_hash` format;
- scans payloads for forbidden identifiers, paths, media references, raw hashes, raw CSV/payload fields, diagnosis, ranking, productivity, and disciplinary language;
- blocks unsafe Sentinela pushes before network transfer.

## Sentinela

Sentinela ingest now:

- accepts only pseudonymized `id_hash` values;
- rejects extra fields by default;
- accepts psychometric data only as aggregate scores;
- rejects item-by-item psychometric answers;
- scans incoming payloads for sensitive identifiers and forbidden operational uses.

## Real Data Preparation

Before doctoral research validation, create a local working directory outside Git for real sanitized files.

Required rules:

- no media;
- no raw file paths;
- no real names;
- no emails;
- no CPF/RG;
- no phone numbers;
- no addresses;
- no raw case/operator/item IDs;
- no raw hashes from evidence;
- no raw CSV line dumps;
- no psychometric item-level responses;
- no diagnosis, ranking, productivity, or disciplinary fields.

The only person/operator identity that may reach SUPREME is a salted 64-character SHA-256 pseudonym.

## Validation Commands

Run from the project root:

```bash
PYTHONPATH=supreme-backend python -m pytest supreme-backend/tests -q
PYTHONPATH=supreme-iped-integration python -m pytest supreme-iped-integration/tests -q
PYTHONPATH=sentinela python -m pytest sentinela/tests -q
```

Expected result after this hardening:

- backend tests pass;
- IPED integration tests pass;
- Sentinela tests pass;
- production use remains dependent on real sanitized validation, baseline, governance, and human review.

## Guardrails

SUPREME is an exposure and governance support system. It is not a diagnostic engine, not a productivity ranking tool, and not a disciplinary decision system. Any result that could affect people or institutions must remain subject to human review, baseline governance, and approved research protocol.
