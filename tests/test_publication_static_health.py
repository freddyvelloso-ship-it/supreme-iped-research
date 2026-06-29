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


def test_sentinela_lab_primary_layer_is_dominant():
    index = (ROOT / "sentinela" / "static" / "index.html").read_text(encoding="utf-8")
    redesign_css = (ROOT / "sentinela" / "static" / "sentinela-redesign.css").read_text(encoding="utf-8")
    primary_css = (ROOT / "sentinela" / "static" / "sentinela-lab-primary.css").read_text(encoding="utf-8")
    ux = (ROOT / "sentinela" / "static" / "sentinela-ux.js").read_text(encoding="utf-8")

    assert 'class="login-screen sentinela-lab-login"' in index
    assert "/sentinela/static/sentinela-lab-primary.css" in index
    assert "body.sentinela-lab-primary" in primary_css
    assert "SENTINELA_LAB_PRIMARY" in ux
    assert "ensureLabShell" in ux
    assert "function showAuthenticatedShell()" in index
    assert "function showLoginShell()" in index
    assert "if (loginScreen) loginScreen.style.display = 'none';" in index
    assert "if (appShell) appShell.style.display = 'grid';" in index
    assert "document.getElementById('login-screen').style.display = ''" not in index
    assert "if (!hasAuthenticatedSession())" in index
    assert 'panel.className = "ux-decision-panel"' not in ux
    assert "addDashboardUX" not in ux
    assert "body.sentinela-authenticated #login-screen.sentinela-lab-login" in redesign_css
    assert "display: none !important" in redesign_css
    assert '<div class="login-card-scan"' not in index
    assert '<div class="biometric-field"' not in index


def test_war_room_dashboard_return_does_not_flash_login_shell():
    index = (ROOT / "sentinela" / "static" / "index.html").read_text(encoding="utf-8")
    redesign_css = (ROOT / "sentinela" / "static" / "sentinela-redesign.css").read_text(encoding="utf-8")
    war_room = (ROOT / "sentinela" / "static" / "war_room.html").read_text(encoding="utf-8")

    assert 'href="/sentinela#overview"' in war_room
    assert "const DASHBOARD_URL = '/sentinela#overview';" in war_room
    assert "from=warroom" not in war_room
    assert "document.body.classList.add('auth-restoring');" in index
    assert "if (restoringLogin) restoringLogin.style.display = 'none';" in index
    assert "body.auth-restoring #login-screen.sentinela-lab-login" in redesign_css
    assert "visibility: hidden !important" in redesign_css


def test_sentinela_lab_menu_is_not_fixed_or_cut_by_header():
    primary_css = (ROOT / "sentinela" / "static" / "sentinela-lab-primary.css").read_text(encoding="utf-8")

    nav_block = primary_css.split("body.sentinela-lab-primary .nav {", 1)[1].split("}", 1)[0]
    main_block = primary_css.split("body.sentinela-lab-primary .main {", 1)[1].split("}", 1)[0]
    assert "position: sticky !important" in nav_block
    assert "position: fixed !important" not in nav_block
    assert "grid-row: 2 !important" in nav_block
    assert "grid-row: 2 !important" in main_block
    assert "--lab-sidebar: #17435a;" in primary_css
    assert "--lab-sidebar-deep: #0f2f42;" in primary_css
    assert "linear-gradient(180deg, var(--lab-sidebar), var(--lab-sidebar-deep))" in nav_block
    assert "background: #e9f7fb !important;" in primary_css


def test_sentinela_participants_cards_are_readable():
    primary_css = (ROOT / "sentinela" / "static" / "sentinela-lab-primary.css").read_text(encoding="utf-8")

    assert "body.sentinela-lab-primary .foc-person-card" in primary_css
    assert "min-height: 264px !important;" in primary_css
    assert "grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)) !important;" in primary_css
    assert "body.sentinela-lab-primary .foc-person-metrics" in primary_css
    assert "body.sentinela-lab-primary .foc-person-status" in primary_css


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
    assert "function pseudonymize(value)" in gate
    assert 'digest("hex")' in gate
    assert "const idHash = pseudonymize(`journey-gate-${Date.now()}`);" in gate
    assert "const idHash = `journey-gate-${Date.now()}`;" not in gate
