"""Codex authentication boundary for GAIA.

GAIA delegates ChatGPT/Codex OAuth ownership to the Codex CLI.  This module
checks the CLI session status and starts the official login command, but never
reads or copies Codex access or refresh tokens.
"""
from __future__ import annotations

import shutil
import subprocess


CODEX_AUTH_SOURCE = "oauth_codex_cli"
CODEX_OAUTH_TOKEN_SENTINEL = "__gaia_codex_cli__"


def codex_cli_path() -> str | None:
    """Return the installed Codex executable without inspecting its auth store."""

    return shutil.which("codex")


def is_codex_cli_authenticated(*, timeout: float = 10.0) -> bool:
    """Ask Codex whether its own login session is usable."""

    codex_bin = codex_cli_path()
    if not codex_bin:
        return False
    try:
        completed = subprocess.run(
            [codex_bin, "login", "status"],
            check=False,
            capture_output=True,
            text=True,
            timeout=max(1.0, float(timeout)),
        )
    except (OSError, subprocess.SubprocessError, ValueError):
        return False
    return completed.returncode == 0


def run_codex_login(*, timeout: float | None = None) -> bool:
    """Run the official Codex login flow and verify the resulting session."""

    codex_bin = codex_cli_path()
    if not codex_bin:
        return False
    try:
        completed = subprocess.run(
            [codex_bin, "login"],
            check=False,
            timeout=timeout,
        )
    except (OSError, subprocess.SubprocessError, ValueError):
        return False
    return completed.returncode == 0 and is_codex_cli_authenticated()
