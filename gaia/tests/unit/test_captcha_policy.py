from __future__ import annotations

import json

from gaia.src.phase4.captcha_solver import CaptchaSolver


class _VisionClient:
    def __init__(self, payload: dict[str, object]) -> None:
        self.payload = payload

    def analyze_with_vision(self, prompt: str, screenshot: str) -> str:
        assert "blocking CAPTCHA" in prompt
        assert screenshot == "screenshot"
        return json.dumps(self.payload)


def test_captcha_policy_detects_but_never_executes_actions() -> None:
    executed: list[tuple[object, ...]] = []
    captured: list[str] = []
    solver = CaptchaSolver(
        vision_client=_VisionClient(
            {
                "detected": True,
                "captcha_type": "recaptcha_v2",
                "confidence": 98,
                "reasoning": "image grid blocks the page",
            }
        ),
        execute_fn=lambda *args, **kwargs: executed.append((*args, kwargs)),
    )

    result = solver.detect_and_handle(
        "screenshot",
        "https://example.com",
        capture_fn=lambda: captured.append("called") or "next",
    )

    assert result.solved is False
    assert result.status == "blocked_user_action"
    assert result.reasoning == "image grid blocks the page"
    assert executed == []
    assert captured == []


def test_captcha_policy_leaves_clear_pages_alone() -> None:
    solver = CaptchaSolver(
        vision_client=_VisionClient(
            {
                "detected": False,
                "captcha_type": "none",
                "confidence": 99,
                "reasoning": "ordinary login form",
            }
        ),
        execute_fn=lambda *args, **kwargs: None,
    )

    result = solver.detect_and_handle("screenshot")

    assert result.solved is False
    assert result.status == "no_captcha"
