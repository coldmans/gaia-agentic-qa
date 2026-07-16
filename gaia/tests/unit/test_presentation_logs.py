from __future__ import annotations

from gaia.src.gui.presentation_logs import (
    audience_log_line,
    detect_log_level,
    format_log_line_html,
    strip_worker_log_prefix,
)


def test_detect_log_level_classifies_failure_warning_and_info() -> None:
    assert detect_log_level("액션 실패") == "ERROR"
    assert detect_log_level("⚠️ 사용자 조치 필요") == "WARN"
    assert detect_log_level("화면 분석 중") == "INFO"


def test_audience_log_hides_runtime_details_and_summarizes_decision() -> None:
    assert audience_log_line('14:22:04.288 INFO {"runtime_policy": {}}') is None
    assert audience_log_line("14:22:04.288 INFO LLM 결정: click - e42") == ("판단: 클릭 대상 선택", "INFO")


def test_audience_log_reports_recovery_without_raw_browser_error() -> None:
    line = "14:22:04.288 ERROR 액션 실패: div intercepts pointer events (covered)"

    assert audience_log_line(line) == ("가려진 UI 감지 -> 재탐색 후 재시도", "RECOVERY")


def test_format_log_line_html_escapes_message_and_preserves_timestamp() -> None:
    html_line, level = format_log_line_html("완료 <script>", ts="12:00:00.000")

    assert level == "INFO"
    assert "12:00:00.000" in html_line
    assert "&lt;script&gt;" in html_line
    assert "<script>" not in html_line


def test_strip_worker_log_prefix_handles_millisecond_timestamp() -> None:
    assert strip_worker_log_prefix("14:22:04.288 SUCCESS 목표 달성") == "14:22:04.288 SUCCESS 목표 달성"
    assert strip_worker_log_prefix("14:22:04.288 INFO 판단: 상태 안정화") == "판단: 상태 안정화"
