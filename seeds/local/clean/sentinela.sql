-- SENTINELA local clean seed.
-- Password for local.master@supreme.local is: supreme-local-admin
-- The legacy SHA-256 hash is intentionally local-only; first login rehashes it with bcrypt.

DELETE FROM red_flags WHERE id_hash LIKE 'phase1-%';
DELETE FROM psico_submissions WHERE id_hash LIKE 'phase1-%';
DELETE FROM ieo_windows WHERE id_hash LIKE 'phase1-%';
DELETE FROM participant_lifecycle WHERE id_hash LIKE 'phase1-%';
DELETE FROM user_scope_assignments
WHERE user_id IN (
    SELECT id FROM sentinela_users WHERE email IN ('admin@supreme.local')
);
DELETE FROM sentinela_users WHERE email IN ('admin@supreme.local');

INSERT INTO sentinela_users(email, password_hash, role)
VALUES (
    'local.master@supreme.local',
    '1ebec9d8ff4c2a6148d65354c4fc998f0ce2469c64943ceb6b422d4988183ae4',
    'master'
)
ON CONFLICT (email) DO UPDATE SET
    password_hash = EXCLUDED.password_hash,
    role = EXCLUDED.role;
