-- SENTINELA becomes a viewer of SUPREME analytical outputs.

ALTER TABLE red_flags
    ADD COLUMN IF NOT EXISTS algorithm_version TEXT,
    ADD COLUMN IF NOT EXISTS algorithm_parameters JSONB;

ALTER TABLE ieo_windows
    ADD COLUMN IF NOT EXISTS algorithm_version TEXT,
    ADD COLUMN IF NOT EXISTS algorithm_parameters JSONB;
