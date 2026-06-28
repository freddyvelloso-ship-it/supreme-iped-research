-- Migration 009: operational longitudinal profile of the forensic expert.
-- SUPREME remains the source of truth. This is not a clinical diagnosis.

CREATE TABLE IF NOT EXISTS longitudinal_profiles (
    id_hash TEXT PRIMARY KEY,
    profile_class TEXT NOT NULL CHECK (profile_class IN ('medio','resiliente','vulneravel','junior','senior')),
    profile_label TEXT NOT NULL,
    profile_confidence FLOAT NOT NULL CHECK (profile_confidence >= 0 AND profile_confidence <= 1),
    profile_evidence JSONB NOT NULL DEFAULT '{}'::jsonb,
    baseline_version INTEGER,
    algorithm_version TEXT NOT NULL,
    algorithm_parameters JSONB NOT NULL DEFAULT '{}'::jsonb,
    classified_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_longitudinal_profiles_class ON longitudinal_profiles(profile_class);
CREATE INDEX IF NOT EXISTS idx_longitudinal_profiles_classified_at ON longitudinal_profiles(classified_at);

ALTER TABLE longitudinal_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE longitudinal_profiles FORCE ROW LEVEL SECURITY;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies
        WHERE schemaname = 'public'
          AND tablename = 'longitudinal_profiles'
          AND policyname = 'operator_all_longitudinal_profiles'
    ) THEN
        CREATE POLICY operator_all_longitudinal_profiles
            ON longitudinal_profiles TO supreme_operator
            USING (true) WITH CHECK (true);
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_policies
        WHERE schemaname = 'public'
          AND tablename = 'longitudinal_profiles'
          AND policyname = 'analytics_read_longitudinal_profiles'
    ) THEN
        CREATE POLICY analytics_read_longitudinal_profiles
            ON longitudinal_profiles FOR SELECT TO supreme_analytics
            USING (true);
    END IF;
END $$;

COMMENT ON TABLE longitudinal_profiles IS 'Perfil operacional longitudinal do perito calculado pelo SUPREME; nao e diagnostico clinico.';
