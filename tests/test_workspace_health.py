from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TMP = ROOT / "tmp" / "pytest"


def run_isolated_pytest(project: str, *, pythonpath: str | None = None) -> None:
    env = os.environ.copy()
    env.pop("PYTHONPATH", None)
    base_temp = TMP / project
    env["TEMP"] = str(base_temp)
    env["TMP"] = str(base_temp)
    if pythonpath:
        env["PYTHONPATH"] = pythonpath
    base_temp.mkdir(parents=True, exist_ok=True)

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "-q",
            "-p",
            "no:cacheprovider",
            "--basetemp",
            str(base_temp / "run"),
        ],
        cwd=ROOT / project,
        env=env,
        text=True,
        capture_output=True,
        timeout=180,
        check=False,
    )
    assert result.returncode == 0, (
        f"{project} pytest failed\nSTDOUT:\n{result.stdout[-4000:]}\nSTDERR:\n{result.stderr[-4000:]}"
    )


def test_sentinela_suite_isolated():
    run_isolated_pytest("sentinela", pythonpath="src")


def test_supreme_backend_suite_isolated():
    run_isolated_pytest("supreme-backend", pythonpath="src")


def test_iped_integration_suite_isolated():
    run_isolated_pytest("supreme-iped-integration")
