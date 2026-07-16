from __future__ import annotations

from types import SimpleNamespace

from gaia import codex_auth


def test_codex_login_status_delegates_to_cli(monkeypatch) -> None:
    calls: list[list[str]] = []

    def fake_run(command, **_kwargs):
        calls.append(list(command))
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(codex_auth.shutil, "which", lambda name: "/usr/local/bin/codex" if name == "codex" else None)
    monkeypatch.setattr(codex_auth.subprocess, "run", fake_run)

    assert codex_auth.is_codex_cli_authenticated() is True
    assert calls == [["/usr/local/bin/codex", "login", "status"]]


def test_codex_login_verifies_session_without_reading_credentials(monkeypatch) -> None:
    calls: list[list[str]] = []

    def fake_run(command, **_kwargs):
        calls.append(list(command))
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(codex_auth.shutil, "which", lambda name: "/usr/local/bin/codex" if name == "codex" else None)
    monkeypatch.setattr(codex_auth.subprocess, "run", fake_run)

    assert codex_auth.run_codex_login() is True
    assert calls == [
        ["/usr/local/bin/codex", "login"],
        ["/usr/local/bin/codex", "login", "status"],
    ]
