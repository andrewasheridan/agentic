"""Tests for strategic_compact.py hook."""

import io
import json
import os
import pathlib
import sys
import time
from typing import Any

import pytest

# ---------------------------------------------------------------------------
# Module import: add the hooks directory to sys.path so we can import by name.
# ---------------------------------------------------------------------------
_HOOKS_DIR = pathlib.Path(__file__).parent
if str(_HOOKS_DIR) not in sys.path:
    sys.path.insert(0, str(_HOOKS_DIR))

import strategic_compact  # noqa: E402

_get_env_int = strategic_compact._get_env_int
_sanitise_session_id = strategic_compact._sanitise_session_id


# ===========================================================================
# Helpers
# ===========================================================================


def _build_stdin(payload: Any) -> io.BytesIO:
    return io.BytesIO(json.dumps(payload).encode())


class _FakeStdin:
    """Minimal stdin replacement with a .buffer attribute."""

    def __init__(self, data: bytes) -> None:
        self.buffer = io.BytesIO(data)


class _CapturingStdout:
    """Minimal stdout replacement that records write() calls."""

    def __init__(self) -> None:
        self._parts: list[str] = []

    def write(self, s: str) -> None:
        self._parts.append(s)

    def flush(self) -> None:
        pass

    def getvalue(self) -> str:
        return "".join(self._parts)


async def _run_main(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: pathlib.Path,
    *,
    payload: Any = None,
    raw_stdin: bytes | None = None,
    env: dict[str, str] | None = None,
) -> str:
    """Patch environment, stdin, stdout, and tempdir; run main(); return stdout."""
    # Redirect tempfile.gettempdir so counter files land in tmp_path.
    monkeypatch.setattr("strategic_compact.tempfile.gettempdir", lambda: str(tmp_path))

    # Build stdin bytes.
    if raw_stdin is not None:
        stdin_bytes = raw_stdin
    elif payload is not None:
        stdin_bytes = json.dumps(payload).encode()
    else:
        stdin_bytes = b"{}"

    monkeypatch.setattr(sys, "stdin", _FakeStdin(stdin_bytes))

    # Apply extra env vars (undo automatically via monkeypatch).
    if env:
        for k, v in env.items():
            monkeypatch.setenv(k, v)

    # Capture stdout.
    capturing_stdout = _CapturingStdout()
    monkeypatch.setattr(sys, "stdout", capturing_stdout)

    await strategic_compact.main()

    return capturing_stdout.getvalue()


# ===========================================================================
# Unit tests — pure functions (sync)
# ===========================================================================


def test_get_env_int_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("MY_VAR", raising=False)
    assert _get_env_int("MY_VAR", 42, 1, 100) == 42


def test_get_env_int_valid(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MY_VAR", "7")
    assert _get_env_int("MY_VAR", 42, 1, 100) == 7


def test_get_env_int_clamp_low(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MY_VAR", "0")
    assert _get_env_int("MY_VAR", 10, 5, 100) == 5


def test_get_env_int_clamp_high(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MY_VAR", "999")
    assert _get_env_int("MY_VAR", 10, 1, 50) == 50


def test_get_env_int_invalid(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MY_VAR", "not-a-number")
    assert _get_env_int("MY_VAR", 99, 1, 1000) == 99


def test_sanitise_session_id_clean() -> None:
    assert _sanitise_session_id("abc123_-XYZ") == "abc123_-XYZ"


def test_sanitise_session_id_strips_special() -> None:
    result = _sanitise_session_id("hello world!@#$%")
    assert result == "helloworld"


def test_sanitise_session_id_empty_fallback() -> None:
    assert _sanitise_session_id("") == "default"


def test_sanitise_session_id_all_special_fallback() -> None:
    assert _sanitise_session_id("!@#$%^&*()") == "default"


# ===========================================================================
# Async integration tests — main()
# ===========================================================================


@pytest.mark.asyncio
async def test_counter_increments(
    monkeypatch: pytest.MonkeyPatch, tmp_path: pathlib.Path
) -> None:
    session = "testsess"
    counter_file = tmp_path / f"claude-tool-count-{session}"
    payload = {"session_id": session}

    for expected in range(1, 4):
        await _run_main(
            monkeypatch, tmp_path, payload=payload, env={"COMPACT_THRESHOLD": "1000"}
        )
        assert counter_file.read_text() == str(expected)


@pytest.mark.asyncio
async def test_no_output_below_threshold(
    monkeypatch: pytest.MonkeyPatch, tmp_path: pathlib.Path
) -> None:
    payload = {"session_id": "below"}
    # threshold=5 — run 4 times; expect no stdout each time.
    for _ in range(4):
        out = await _run_main(
            monkeypatch,
            tmp_path,
            payload=payload,
            env={"COMPACT_THRESHOLD": "5", "COMPACT_REPEAT_INTERVAL": "5"},
        )
        assert out == ""


@pytest.mark.asyncio
async def test_suggestion_at_threshold(
    monkeypatch: pytest.MonkeyPatch, tmp_path: pathlib.Path
) -> None:
    session = "thresh"
    payload = {"session_id": session}

    # Pre-seed so the next call lands exactly on threshold=3.
    counter_file = tmp_path / f"claude-tool-count-{session}"
    counter_file.write_text("2")

    out = await _run_main(
        monkeypatch,
        tmp_path,
        payload=payload,
        env={"COMPACT_THRESHOLD": "3", "COMPACT_REPEAT_INTERVAL": "10"},
    )

    assert out != ""
    data = json.loads(out)
    inner = data["hookSpecificOutput"]
    assert inner["permissionDecision"] == "approve"
    assert "good time" in inner["permissionDecisionReason"]


@pytest.mark.asyncio
async def test_suggestion_at_repeat_interval(
    monkeypatch: pytest.MonkeyPatch, tmp_path: pathlib.Path
) -> None:
    session = "repeat"
    threshold = 3
    interval = 5
    payload = {"session_id": session}

    # Pre-seed so the next call lands at threshold + interval.
    counter_file = tmp_path / f"claude-tool-count-{session}"
    counter_file.write_text(str(threshold + interval - 1))

    out = await _run_main(
        monkeypatch,
        tmp_path,
        payload=payload,
        env={
            "COMPACT_THRESHOLD": str(threshold),
            "COMPACT_REPEAT_INTERVAL": str(interval),
        },
    )

    assert out != ""
    data = json.loads(out)
    reason = data["hookSpecificOutput"]["permissionDecisionReason"]
    assert "consider /compact" in reason


@pytest.mark.asyncio
async def test_no_suggestion_between_intervals(
    monkeypatch: pytest.MonkeyPatch, tmp_path: pathlib.Path
) -> None:
    session = "between"
    threshold = 3
    interval = 5
    payload = {"session_id": session}

    # Pre-seed so the next call is threshold + 1 (not a repeat boundary).
    counter_file = tmp_path / f"claude-tool-count-{session}"
    counter_file.write_text(str(threshold))  # next call → threshold + 1

    out = await _run_main(
        monkeypatch,
        tmp_path,
        payload=payload,
        env={
            "COMPACT_THRESHOLD": str(threshold),
            "COMPACT_REPEAT_INTERVAL": str(interval),
        },
    )

    assert out == ""


@pytest.mark.asyncio
async def test_counter_resets_after_ttl(
    monkeypatch: pytest.MonkeyPatch, tmp_path: pathlib.Path
) -> None:
    session = "ttlreset"
    payload = {"session_id": session}
    counter_file = tmp_path / f"claude-tool-count-{session}"

    # Write a high count and backdate the mtime to 2 hours ago (TTL = 1 hour).
    counter_file.write_text("99")
    past = time.time() - 7200
    os.utime(counter_file, (past, past))

    await _run_main(
        monkeypatch,
        tmp_path,
        payload=payload,
        env={"COMPACT_THRESHOLD": "1000", "COUNTER_TTL_HOURS": "1"},
    )

    # Counter must have reset to 1 rather than incrementing to 100.
    assert counter_file.read_text() == "1"


@pytest.mark.asyncio
async def test_stale_files_cleaned_up(
    monkeypatch: pytest.MonkeyPatch, tmp_path: pathlib.Path
) -> None:
    # Create a stale counter file for a different session.
    stale_file = tmp_path / "claude-tool-count-old"
    stale_file.write_text("42")
    past = time.time() - 7200  # 2 hours ago
    os.utime(stale_file, (past, past))

    payload = {"session_id": "newsession"}
    await _run_main(
        monkeypatch,
        tmp_path,
        payload=payload,
        env={"COMPACT_THRESHOLD": "1000", "COUNTER_TTL_HOURS": "1"},
    )

    assert not stale_file.exists()


@pytest.mark.asyncio
async def test_invalid_json_stdin(
    monkeypatch: pytest.MonkeyPatch, tmp_path: pathlib.Path
) -> None:
    # Malformed JSON should not crash; should fall back to "default" session.
    await _run_main(
        monkeypatch,
        tmp_path,
        raw_stdin=b"{not valid json!!!}",
        env={"COMPACT_THRESHOLD": "1000"},
    )
    counter_file = tmp_path / "claude-tool-count-default"
    assert counter_file.exists()
    assert counter_file.read_text() == "1"


@pytest.mark.asyncio
async def test_empty_stdin(
    monkeypatch: pytest.MonkeyPatch, tmp_path: pathlib.Path
) -> None:
    # Empty stdin should not crash; should fall back to "default" session.
    await _run_main(
        monkeypatch,
        tmp_path,
        raw_stdin=b"",
        env={"COMPACT_THRESHOLD": "1000"},
    )
    counter_file = tmp_path / "claude-tool-count-default"
    assert counter_file.exists()
    assert counter_file.read_text() == "1"


@pytest.mark.asyncio
async def test_session_isolation(
    monkeypatch: pytest.MonkeyPatch, tmp_path: pathlib.Path
) -> None:
    payload_a = {"session_id": "sessionA"}
    payload_b = {"session_id": "sessionB"}

    for _ in range(3):
        await _run_main(
            monkeypatch, tmp_path, payload=payload_a, env={"COMPACT_THRESHOLD": "1000"}
        )
    for _ in range(5):
        await _run_main(
            monkeypatch, tmp_path, payload=payload_b, env={"COMPACT_THRESHOLD": "1000"}
        )

    file_a = tmp_path / "claude-tool-count-sessionA"
    file_b = tmp_path / "claude-tool-count-sessionB"

    assert file_a.read_text() == "3"
    assert file_b.read_text() == "5"
