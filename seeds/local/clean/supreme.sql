-- SUPREME V4 local clean seed.
-- Keeps the database usable and removes only deterministic Phase 1 local data.

DELETE FROM critical_load_flags WHERE id_hash LIKE 'phase1-%';
DELETE FROM psi_scores WHERE id_hash LIKE 'phase1-%';
DELETE FROM psychometric_submissions WHERE id_hash LIKE 'phase1-%';
DELETE FROM instrument_schedule WHERE id_hash LIKE 'phase1-%';
DELETE FROM baseline_parameters WHERE id_hash LIKE 'phase1-%';
DELETE FROM ieo_logs WHERE id_hash LIKE 'phase1-%';
DELETE FROM window_metrics WHERE id_hash LIKE 'phase1-%';
DELETE FROM sessions WHERE id_hash LIKE 'phase1-%';
DELETE FROM events_raw WHERE id_hash LIKE 'phase1-%';
DELETE FROM system_health_logs WHERE id_hash LIKE 'phase1-%';
DELETE FROM dead_letter_queue WHERE id_hash LIKE 'phase1-%';
DELETE FROM subject_consents WHERE id_hash LIKE 'phase1-%';
