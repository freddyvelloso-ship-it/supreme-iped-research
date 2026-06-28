-- SENTINELA viewer cache for SUPREME-computed longitudinal profiles.
-- SENTINELA does not calculate or recompute these categories.

CREATE TABLE IF NOT EXISTS longitudinal_profiles (
    id_hash TEXT PRIMARY KEY,
    profile_class TEXT NOT NULL CHECK (profile_class IN ('medio','resiliente','vulneravel','junior','senior')),
    profile_label TEXT NOT NULL,
    profile_confidence FLOAT NOT NULL CHECK (profile_confidence >= 0 AND profile_confidence <= 1),
    profile_evidence JSONB NOT NULL DEFAULT '{}'::jsonb,
    baseline_version INTEGER,
    algorithm_version TEXT NOT NULL,
    algorithm_parameters JSONB NOT NULL DEFAULT '{}'::jsonb,
    classified_at TIMESTAMPTZ NOT NULL,
    received_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_sentinela_longitudinal_profiles_class ON longitudinal_profiles(profile_class);
CREATE INDEX IF NOT EXISTS idx_sentinela_longitudinal_profiles_classified_at ON longitudinal_profiles(classified_at);

COMMENT ON TABLE longitudinal_profiles IS 'Viewer cache do perfil operacional longitudinal calculado pelo SUPREME; nao e diagnostico clinico.';
