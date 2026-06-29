from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_launcher_blocks_post_session_when_iped_does_not_start():
    launcher = (ROOT / "LAUNCHER_IPED.ps1").read_text(encoding="utf-8")

    guard_index = launcher.index("if (-not $ipedStarted)")
    post_session_index = launcher.index("# Pos-sessao")
    assert "$ipedStarted = $false" in launcher
    assert "$ipedStarted = $true" in launcher
    assert guard_index < post_session_index
    assert "O IPED nao foi iniciado. O fluxo pos-sessao nao sera aberto." in launcher
    assert "encerrou imediatamente. O fluxo pos-sessao nao sera aberto." in launcher


def test_sentinela_login_not_hybrid_after_authentication():
    index = (ROOT / "sentinela" / "static" / "index.html").read_text(encoding="utf-8")
    css = (ROOT / "sentinela" / "static" / "sentinela-redesign.css").read_text(encoding="utf-8")

    assert 'class="login-screen sentinela-lab-login"' in index
    assert "body.sentinela-authenticated #login-screen.sentinela-lab-login" in css
    assert "display: none !important" in css
    assert '<div class="login-card-scan"' not in index
    assert '<div class="biometric-field"' not in index


def test_login_i18n_has_no_fixed_hero_title():
    index = (ROOT / "sentinela" / "static" / "index.html").read_text(encoding="utf-8")
    ux = (ROOT / "sentinela" / "static" / "sentinela-ux.js").read_text(encoding="utf-8")

    assert '<h2 data-i18n="heroTitle">' in index
    assert 'heroTitle: "Governança longitudinal da exposição em perícia digital"' in ux
    assert 'heroTitle: "Longitudinal governance of digital forensics exposure"' in ux
    assert 'heroTitle: "Gobernanza longitudinal de la exposición en pericia digital"' in ux


def test_iped_journey_gate_uses_hex64_pseudonym_for_ingest_events():
    gate = (ROOT / "scripts" / "iped_journey_gate.mjs").read_text(encoding="utf-8")

    assert 'import { createHash } from "node:crypto";' in gate
    assert 'function pseudonymize(value)' in gate
    assert 'digest("hex")' in gate
    assert "const idHash = pseudonymize(`journey-gate-${Date.now()}`);" in gate
    assert "const idHash = `journey-gate-${Date.now()}`;" not in gate
