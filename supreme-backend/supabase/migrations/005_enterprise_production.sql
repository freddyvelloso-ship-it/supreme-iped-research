-- Migration 005: SUPREME produção institucional / enterprise

ALTER TABLE ieo_logs
    ADD COLUMN IF NOT EXISTS algorithm_version TEXT NOT NULL DEFAULT 'SUPREME-ANALYTICS-1.0.0',
    ADD COLUMN IF NOT EXISTS algorithm_parameters JSONB NOT NULL DEFAULT '{}'::jsonb;

CREATE TABLE IF NOT EXISTS audit_log (
    audit_id BIGSERIAL PRIMARY KEY,
    actor TEXT NOT NULL DEFAULT 'system',
    action TEXT NOT NULL,
    subject_id_hash TEXT,
    resource TEXT,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_audit_subject ON audit_log(subject_id_hash);
CREATE INDEX IF NOT EXISTS idx_audit_created ON audit_log(created_at);

CREATE TABLE IF NOT EXISTS algorithm_registry (
    algorithm_version TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    parameters JSONB NOT NULL DEFAULT '{}'::jsonb,
    git_commit TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    is_active BOOLEAN NOT NULL DEFAULT FALSE
);

INSERT INTO algorithm_registry(algorithm_version, name, parameters, is_active)
VALUES ('SUPREME-ANALYTICS-1.0.0', 'Unified SUPREME analytical engine for IEO, PSI and red flags', '{"ieo":{"z_t":0.5,"z_e":0.3,"z_v":0.2,"z_d_delta":0.1,"logistic_k":1.0,"logistic_x0":1.0},"psi":{"z_dass":0.35,"z_olbi":0.30,"z_srq":0.20,"z_panas_neg":0.15,"psi_threshold":0.0,"oei_threshold":0.0,"min_history_for_baseline":4},"red_flags":{"exposure_z_threshold":1.5,"major_exposure_z_threshold":2.0,"psychometric_high_z_threshold":1.0,"chronic_windows":2}}'::jsonb, TRUE)
ON CONFLICT (algorithm_version) DO NOTHING;

CREATE OR REPLACE FUNCTION log_subject_erasure(p_subject TEXT, p_actor TEXT DEFAULT 'system') RETURNS VOID AS $$
BEGIN
    INSERT INTO audit_log(actor, action, subject_id_hash, resource, metadata)
    VALUES (p_actor, 'subject_erasure_requested', p_subject, 'all_subject_tables', '{}'::jsonb);
END;
$$ LANGUAGE plpgsql;
