"""Detection-only CAPTCHA boundary for the public GAIA runtime.

CAPTCHA and anti-bot challenges require a human operator. This module keeps the
legacy ``CaptchaSolver`` API so existing integrations can detect a challenge,
but it never clicks, types, drags, or attempts to solve one.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)


@dataclass
class CaptchaDetectionResult:
    detected: bool = False
    captcha_type: str = "none"
    confidence: int = 0
    reasoning: str = ""


@dataclass
class CaptchaStepResult:
    solved: bool = False
    status: str = "pending"
    attempts: int = 0
    reasoning: str = ""


class CaptchaSolver:
    """Detect CAPTCHA surfaces without interacting with them."""

    def __init__(
        self,
        vision_client: Any,
        execute_fn: Callable[..., Any],
        mcp_host_url: str = "",
        session_id: str = "",
        max_attempts: int = 1,
        log_fn: Optional[Callable[[str], None]] = None,
    ) -> None:
        # Keep the constructor contract for downstream callers. Action-related
        # arguments are deliberately not retained or invoked.
        del execute_fn, mcp_host_url, session_id, max_attempts
        self._vision = vision_client
        self._log = log_fn or (lambda message: logger.info(message))

    def detect_captcha(
        self,
        screenshot_b64: str,
        page_url: str = "",
    ) -> CaptchaDetectionResult:
        """Classify whether a screenshot contains a blocking challenge."""
        prompt = f"""Analyze this screenshot for a blocking CAPTCHA or anti-bot challenge.

Page URL: {page_url or "unknown"}

Look for hCaptcha, reCAPTCHA, Cloudflare Turnstile, text/image CAPTCHA fields,
slider puzzles, or equivalent security verification. Do not treat ordinary
login forms as CAPTCHA.

Return JSON only:
{{
  "detected": true,
  "captcha_type": "hcaptcha | recaptcha_v2 | recaptcha_v3 | text | slider | cloudflare_turnstile | other | none",
  "confidence": 85,
  "reasoning": "brief visual evidence"
}}
"""
        try:
            response = self._vision.analyze_with_vision(prompt, screenshot_b64)
            data = json.loads(response)
            return CaptchaDetectionResult(
                detected=bool(data.get("detected", False)),
                captcha_type=str(data.get("captcha_type", "none")),
                confidence=int(data.get("confidence", 0)),
                reasoning=str(data.get("reasoning", "")),
            )
        except Exception as exc:
            self._log(f"CAPTCHA detection failed: {exc}")
            return CaptchaDetectionResult()

    def detect_and_handle(
        self,
        screenshot: str,
        page_url: str = "",
        capture_fn: Optional[Callable[[], Optional[str]]] = None,
    ) -> CaptchaStepResult:
        """Detect a challenge and return a human-action boundary.

        ``capture_fn`` remains in the signature for compatibility and is never
        called. A detected challenge is intentionally not solved.
        """
        del capture_fn
        detection = self.detect_captcha(screenshot, page_url)
        if not detection.detected:
            return CaptchaStepResult(status="no_captcha")

        self._log(
            "CAPTCHA detected; pausing for human action "
            f"(type={detection.captcha_type}, confidence={detection.confidence})"
        )
        return CaptchaStepResult(
            status="blocked_user_action",
            reasoning=detection.reasoning or detection.captcha_type,
        )
