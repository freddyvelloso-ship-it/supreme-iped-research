-- SENTINELA Phase 2 - granular RBAC and scope model

ALTER TABLE sentinela_users
    DROP CONSTRAINT IF EXISTS sentinela_users_role_check;

UPDATE sentinela_users
SET role = 'pesquisador'
WHERE role = 'pibic';

ALTER TABLE sentinela_users
    ADD CONSTRAINT sentinela_users_role_check
    CHECK (role IN ('master','pesquisador','auditor','operador','leitura_agregada'));

CREATE TABLE IF NOT EXISTS institutions (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS studies (
    id TEXT PRIMARY KEY,
    institution_id TEXT NOT NULL REFERENCES institutions(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS cases (
    id TEXT PRIMARY KEY,
    study_id TEXT NOT NULL REFERENCES studies(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS participant_registry (
    participant_id TEXT PRIMARY KEY,
    id_hash TEXT UNIQUE NOT NULL,
    institution_id TEXT NOT NULL REFERENCES institutions(id) ON DELETE CASCADE,
    study_id TEXT NOT NULL REFERENCES studies(id) ON DELETE CASCADE,
    case_id TEXT NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS user_scope_assignments (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES sentinela_users(id) ON DELETE CASCADE,
    institution_id TEXT REFERENCES institutions(id) ON DELETE CASCADE,
    study_id TEXT REFERENCES studies(id) ON DELETE CASCADE,
    case_id TEXT REFERENCES cases(id) ON DELETE CASCADE,
    participant_id TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    CHECK (
        institution_id IS NOT NULL OR
        study_id IS NOT NULL OR
        case_id IS NOT NULL OR
        participant_id IS NOT NULL
    ),
    UNIQUE (user_id, institution_id, study_id, case_id, participant_id)
);

CREATE TABLE IF NOT EXISTS admin_audit_log (
    id BIGSERIAL PRIMARY KEY,
    actor_email TEXT NOT NULL,
    action TEXT NOT NULL,
    target_type TEXT NOT NULL,
    target_id TEXT NOT NULL,
    detail JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS token_rotation_history (
    id BIGSERIAL PRIMARY KEY,
    token_name TEXT NOT NULL,
    rotated_by TEXT NOT NULL,
    rotated_at TIMESTAMPTZ DEFAULT NOW(),
    evidence_hash TEXT
);

CREATE INDEX IF NOT EXISTS idx_participant_registry_id_hash ON participant_registry(id_hash);
CREATE INDEX IF NOT EXISTS idx_user_scope_assignments_user ON user_scope_assignments(user_id);
CREATE INDEX IF NOT EXISTS idx_admin_audit_log_actor ON admin_audit_log(actor_email);
