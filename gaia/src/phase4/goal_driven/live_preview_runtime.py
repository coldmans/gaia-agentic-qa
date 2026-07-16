from __future__ import annotations

import base64
import os
import tempfile
from pathlib import Path


def live_preview_enabled() -> bool:
    return bool(str(os.getenv("GAIA_LIVE_PREVIEW_PATH", "") or "").strip())


def write_live_preview_screenshot(screenshot_base64: str | None) -> bool:
    """Dump the latest screenshot for the GUI benchmark live-preview watcher."""
    target_text = str(os.getenv("GAIA_LIVE_PREVIEW_PATH", "") or "").strip()
    shot = str(screenshot_base64 or "").strip()
    if not target_text or not shot:
        return False

    if shot.startswith("data:image/") and "," in shot:
        shot = shot.split(",", 1)[1]

    tmp_path: str | None = None
    try:
        payload = base64.b64decode(shot, validate=False)
        if not payload:
            return False
        target = Path(target_text)
        target.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp_path = tempfile.mkstemp(
            prefix=f".{target.name}.",
            suffix=".tmp",
            dir=str(target.parent),
        )
        with os.fdopen(fd, "wb") as tmp:
            tmp.write(payload)
        os.replace(tmp_path, target)
        tmp_path = None
        return True
    except Exception:
        if tmp_path:
            try:
                Path(tmp_path).unlink(missing_ok=True)
            except Exception:
                pass
        return False
