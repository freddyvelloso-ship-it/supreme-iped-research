-- Migration 007: unified SUPREME analytical engine.
-- SUPREME is the source of truth for IEO, PSI and typed red flags.

ALTER TABLE psi_scores
    ADD COLUMN IF NOT EXISTS algorithm_version TEXT NOT NULL DEFAULT 'SUPREME-ANALYTICS-1.0.0',
    ADD COLUMN IF NOT EXISTS algorithm_parameters JSONB NOT NULL DEFAULT '{}'::jsonb;

ALTER TABLE ieo_logs
    ALTER COLUMN algorithm_version SET DEFAULT 'SUPREME-ANALYTICS-1.0.0';

ALTER TABLE psi_scores
    ALTER COLUMN algorithm_version SET DEFAULT 'SUPREME-ANALYTICS-1.0.0';

CREATE TABLE IF NOT EXISTS analytic_red_flags (
    id_hash TEXT NOT NULL,
    window_start DATE NOT NULL,
    flag_type TEXT NOT NULL CHECK (flag_type IN ('reatividade','dissonancia','cronicidade')),
    severity TEXT NOT NULL CHECK (severity IN ('moderado','maior')),
    detail JSONB NOT NULL DEFAULT '{}'::jsonb,
    algorithm_version TEXT NOT NULL,
    algorithm_parameters JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (id_hash, window_start, flag_type)
);

CREATE INDEX IF NOT EXISTS idx_analytic_red_flags_user ON analytic_red_flags(id_hash);
CREATE INDEX IF NOT EXISTS idx_analytic_red_flags_window ON analytic_red_flags(window_start);

ALTER TABLE analytic_red_flags ENABLE ROW LEVEL SECURITY;
ALTER TABLE analytic_red_flags FORCE ROW LEVEL SECURITY;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies
        WHERE schemaname = 'public'
          AND tablename = 'analytic_red_flags'
          AND policyname = 'operator_all_analytic_red_flags'
    ) THEN
        CREATE POLICY operator_all_analytic_red_flags
            ON analytic_red_flags TO supreme_operator
            USING (true) WITH CHECK (true);
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_policies
        WHERE schemaname = 'public'
          AND tablename = 'analytic_red_flags'
          AND policyname = 'analytics_read_analytic_red_flags'
    ) THEN
        CREATE POLICY analytics_read_analytic_red_flags
            ON analytic_red_flags FOR SELECT TO supreme_analytics
            USING (true);
    END IF;
END $$;

INSERT INTO algorithm_registry(algorithm_version, name, parameters, is_active)
VALUES (
    'SUPREME-ANALYTICS-1.0.0',
    'Unified SUPREME analytical engine for IEO, PSI and red flags',
    '{
        "ieo": {"z_t":0.5,"z_e":0.3,"z_v":0.2,"z_d_delta":0.1,"logistic_k":1.0,"logistic_x0":1.0},
        "psi": {"z_dass":0.35,"z_olbi":0.30,"z_srq":0.20,"z_panas_neg":0.15,"psi_threshold":0.0,"oei_threshold":0.0,"min_history_for_baseline":4},
        "red_flags": {"exposure_z_threshold":1.5,"major_exposure_z_threshold":2.0,"psychometric_high_z_threshold":1.0,"chronic_windows":2}
    }'::jsonb,
    TRUE
)
ON CONFLICT (algorithm_version) DO UPDATE SET
    parameters = EXCLUDED.parameters,
    is_active = TRUE;

UPDATE algorithm_registry
SET is_active = FALSE
WHERE algorithm_version <> 'SUPREME-ANALYTICS-1.0.0';

COMMENT ON TABLE analytic_red_flags IS 'Typed red flags computed only by SUPREME unified analytics engine.';
