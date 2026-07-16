from __future__ import annotations

import base64

from gaia.src.phase4.goal_driven.live_preview_runtime import (
    live_preview_enabled,
    write_live_preview_screenshot,
)


def test_live_preview_enabled_tracks_env(monkeypatch, tmp_path) -> None:
    monkeypatch.delenv("GAIA_LIVE_PREVIEW_PATH", raising=False)
    assert live_preview_enabled() is False

    monkeypatch.setenv("GAIA_LIVE_PREVIEW_PATH", str(tmp_path / "latest.png"))
    assert live_preview_enabled() is True


def test_write_live_preview_screenshot_writes_atomic_file(monkeypatch, tmp_path) -> None:
    target = tmp_path / "gui_live_preview" / "latest.png"
    monkeypatch.setenv("GAIA_LIVE_PREVIEW_PATH", str(target))

    payload = b"fake-png-bytes"
    shot = base64.b64encode(payload).decode("ascii")

    assert write_live_preview_screenshot(shot) is True
    assert target.read_bytes() == payload
    assert not list(target.parent.glob("*.tmp"))


def test_write_live_preview_screenshot_accepts_data_url(monkeypatch, tmp_path) -> None:
    target = tmp_path / "latest.png"
    monkeypatch.setenv("GAIA_LIVE_PREVIEW_PATH", str(target))

    payload = b"data-url-image"
    shot = f"data:image/png;base64,{base64.b64encode(payload).decode('ascii')}"

    assert write_live_preview_screenshot(shot) is True
    assert target.read_bytes() == payload
