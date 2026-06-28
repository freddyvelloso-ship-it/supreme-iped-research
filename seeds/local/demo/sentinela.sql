-- SENTINELA local demo seed.
-- These records are visual demo data only and are not used by the deterministic E2E.

INSERT INTO ieo_windows(
    id_hash, window_start, t_minutes, e_events, v_volume, d_density,
    dq_score, ieo_score, ieo_linear, ieo_sat, z_t, z_e, z_v, z_d,
    psi_score, z_dass, z_olbi, z_srq, z_panas_neg, convergence_class
)
VALUES
    ('phase1-demo-analyst-a', '2026-02-12', 95.0, 42, 3800.0, 0.442, 0.95, 1.72, 1.21, 0.55, 1.6, 1.2, 1.8, 0.9, 1.35, 1.1, 1.4, 0.8, 1.2, 'convergencia_critica'),
    ('phase1-demo-analyst-b', '2026-02-12', 35.0, 14, 900.0, 0.400, 0.91, 0.74, 0.38, 0.35, 0.2, 0.1, 0.3, 0.4, 0.25, 0.2, 0.2, 0.1, 0.3, 'baixo_risco')
ON CONFLICT (id_hash, window_start) DO UPDATE SET
    t_minutes = EXCLUDED.t_minutes,
    e_events = EXCLUDED.e_events,
    v_volume = EXCLUDED.v_volume,
    d_density = EXCLUDED.d_density,
    dq_score = EXCLUDED.dq_score,
    ieo_score = EXCLUDED.ieo_score,
    ieo_linear = EXCLUDED.ieo_linear,
    ieo_sat = EXCLUDED.ieo_sat,
    z_t = EXCLUDED.z_t,
    z_e = EXCLUDED.z_e,
    z_v = EXCLUDED.z_v,
    z_d = EXCLUDED.z_d,
    psi_score = EXCLUDED.psi_score,
    z_dass = EXCLUDED.z_dass,
    z_olbi = EXCLUDED.z_olbi,
    z_srq = EXCLUDED.z_srq,
    z_panas_neg = EXCLUDED.z_panas_neg,
    convergence_class = EXCLUDED.convergence_class;

INSERT INTO red_flags(id_hash, window_start, flag_type, severity, detail)
VALUES
    ('phase1-demo-analyst-a', '2026-02-12', 'reatividade', 'maior', '{"source":"seed-local-demo"}'::jsonb),
    ('phase1-demo-analyst-a', '2026-02-12', 'cronicidade', 'moderado', '{"source":"seed-local-demo"}'::jsonb)
ON CONFLICT (id_hash, window_start, flag_type) DO UPDATE SET
    severity = EXCLUDED.severity,
    detail = EXCLUDED.detail;
