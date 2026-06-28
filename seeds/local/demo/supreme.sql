-- SUPREME V4 local demo seed.
-- Demo rows are prefixed with phase1-demo and can be removed by the clean seed.

INSERT INTO subject_consents(id_hash, status, actor, granted_at, updated_at)
VALUES
    ('phase1-demo-analyst-a', 'granted', 'seed:local-demo', NOW(), NOW()),
    ('phase1-demo-analyst-b', 'granted', 'seed:local-demo', NOW(), NOW())
ON CONFLICT (id_hash) DO UPDATE SET
    status = EXCLUDED.status,
    actor = EXCLUDED.actor,
    granted_at = EXCLUDED.granted_at,
    revoked_at = NULL,
    updated_at = NOW();
