"""Pure formatting rules for the desktop presentation log."""
from __future__ import annotations

import html
import re
from datetime import datetime


def detect_log_level(text: str) -> str:
    lower = text.lower()
    if "❌" in text or "fail" in lower or "error" in lower or "오류" in text or "실패" in text:
        return "ERROR"
    if "⚠️" in text or "warn" in lower or "blocked" in lower or "차단" in text:
        return "WARN"
    return "INFO"


def strip_worker_log_prefix(text: str) -> str:
    return re.sub(r"^\d{2}:\d{2}:\d{2}(?:\.\d{3})?\s+(?:INFO|WARN|ERROR)\s+", "", text.strip())


def audience_log_line(message: str) -> tuple[str, str] | None:
    """Condense a raw worker line into one audience-facing presentation event."""

    text = strip_worker_log_prefix(str(message or ""))
    lower = text.lower()
    if not text:
        return None

    hidden_fragments = (
        "schema_version",
        "runner_id",
        "runtime_policy",
        "runtime_isolation",
        "openclaw",
        "base_url",
        "json_path",
        "html_path",
        "llm_ms_",
        "trace_metrics",
        "kpi_metrics",
        "status_counts",
        "failures",
        "blocked",
        "coverage:",
        "127.0.0.1",
        "/users/",
        "file://",
        "cmd:",
        "suite:",
        "target:",
        "metrics:",
        "battle board:",
        "human input:",
        "warm runtime:",
        "서버:",
        "push →",
        "[히스토리]",
        "모니터링 서버",
    )
    if text.startswith(("{", "}", '"')) or any(fragment in lower for fragment in hidden_fragments):
        return None
    if text.startswith("--- Step") or "시작 URL로 이동" in text:
        return None

    if "Human 타이머 시작:" in text:
        return "Human 타이머 시작: " + text.split("Human 타이머 시작:", 1)[1].strip(), "INFO"
    if "벤치 실행 시작:" in text:
        return "GAIA 실행 시작: " + text.split("벤치 실행 시작:", 1)[1].strip(), "INFO"
    if "🎯 목표 시작:" in text:
        return "목표 시작: " + text.split("🎯 목표 시작:", 1)[1].strip(), "INFO"
    if "목표 달성" in text:
        reason = text.split("이유:", 1)[1].strip() if "이유:" in text else text.replace("✅", "").strip()
        return f"목표 달성: {reason}", "SUCCESS"
    if "battle_upload:" in text:
        return "웹 증거 업로드: " + text.split("battle_upload:", 1)[1].strip(), "UPLOAD"
    if "업로드 완료" in text:
        return "웹 보드 업로드 완료", "UPLOAD"
    if "[완료]" in text or "자동화 실행 완료" in text:
        return "GAIA 실행 완료", "SUCCESS"

    if "액션 실패" in text or "not_actionable" in lower or "not interactable" in lower:
        if "covered" in lower or "intercepts pointer events" in lower:
            return "가려진 UI 감지 -> 재탐색 후 재시도", "RECOVERY"
        return "화면 상태 변경 감지 -> 대상 재탐색", "RECOVERY"
    if "not found or not visible" in lower:
        return "화면 상태 변경 감지 -> 최신 화면으로 재탐색", "RECOVERY"
    if "phase 전환" in text:
        return "전략 전환: 화면 수집 -> 실행", "RECOVERY"

    decision_match = re.search(r"LLM 결정:\s*([a-z_]+)\s*-", text)
    if decision_match:
        action = decision_match.group(1)
        action_labels = {
            "click": "클릭 대상 선택",
            "fill": "입력값 준비",
            "type": "입력값 준비",
            "press": "키 입력",
            "scroll": "화면 이동",
            "wait": "상태 안정화 확인",
            "inspect": "화면 관찰",
            "select": "옵션 선택",
        }
        return f"판단: {action_labels.get(action, action)}", "INFO"

    case_match = re.search(r"\]\s+\d+/\d+\s+([A-Z0-9_]+)\s+\.\.\.", text)
    if case_match:
        return f"케이스 실행: {case_match.group(1)}", "INFO"
    return None


def format_log_line_html(
    message: str,
    *,
    ts: str | None = None,
    audience_mode: bool = False,
) -> tuple[str, str]:
    if ts is None:
        ts = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    text = str(message or "")
    if audience_mode:
        audience_line = audience_log_line(text)
        if audience_line is None:
            return "", "HIDDEN"
        text, level = audience_line
    else:
        level = detect_log_level(text)

    if level == "ERROR":
        level_color, msg_color = "#ef4444", "#fca5a5"
    elif level == "WARN":
        level_color, msg_color = "#f59e0b", "#fde68a"
    elif level == "RECOVERY":
        level_color, msg_color = "#38bdf8", "#bae6fd"
    elif level == "UPLOAD":
        level_color, msg_color = "#a78bfa", "#ddd6fe"
    elif level == "SUCCESS" or "✅" in text or "success" in text.lower() or "pass" in text.lower() or "성공" in text or "달성" in text:
        level_color, msg_color = "#1f9d6a", "#86efac"
    else:
        level_color, msg_color = "#1f9d6a", "#e2e8f0"
    safe_text = html.escape(text)
    html_line = (
        f'<span style="color:#94a3b8;">{ts}</span>  '
        f'<span style="color:{level_color}; font-weight:700;">{level}</span>  '
        f'<span style="color:{msg_color};">{safe_text}</span>'
    )
    return html_line, level
