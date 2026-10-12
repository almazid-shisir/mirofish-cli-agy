"""Unit tests for MiroFish MCP server tools."""

import pytest
from app.mcp_server import (
    mirofish_doctor,
    mirofish_list_runs,
    mirofish_get_status,
    mirofish_get_verdict,
    mirofish_get_report,
)


def test_mcp_doctor():
    result = mirofish_doctor()
    assert result["engine"] == "MiroFish CLI AGY"
    assert result["llm_provider"] in ("agy-cli", "claude-cli", "codex-cli")
    assert "ready" in result


def test_mcp_list_runs():
    runs = mirofish_list_runs()
    assert isinstance(runs, list)


def test_mcp_nonexistent_run():
    status = mirofish_get_status("run_nonexistent_12345")
    assert status["status"] == "not_found"

    verdict = mirofish_get_verdict("run_nonexistent_12345")
    assert "error" in verdict

    report = mirofish_get_report("run_nonexistent_12345")
    assert "error" in report
