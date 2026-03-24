#!/usr/bin/env python3.14
"""Claude Code PreToolUse hook: suggests /compact at tool-call thresholds.

Reads a JSON payload from stdin, increments a per-session tool-call counter
stored in a temp file, and writes a JSON suggestion to stdout when the count
hits the configured threshold or a repeat interval. Never blocks a tool call.
"""

import asyncio
import fcntl
import json
import os
import pathlib
import re
import sys
import tempfile
import time


def _get_env_int(name: str, default: int, lo: int, hi: int) -> int:
    """Read an integer environment variable and clamp it to [lo, hi].

    Args:
        name: Environment variable name.
        default: Value to use when the variable is absent or invalid.
        lo: Inclusive lower bound.
        hi: Inclusive upper bound.

    Returns:
        The clamped integer value.
    """
    raw = os.environ.get(name, "")
    try:
        value = int(raw)
    except ValueError:
        value = default
    return max(lo, min(hi, value))


def _sanitise_session_id(raw: str) -> str:
    """Return a filesystem-safe session id.

    Keeps only ``[a-zA-Z0-9_-]`` characters. Falls back to ``"default"`` when
    the result would be empty.

    Args:
        raw: Arbitrary string from the hook payload.

    Returns:
        A non-empty, filesystem-safe session identifier.
    """
    sanitised = re.sub(r"[^a-zA-Z0-9_\-]", "", raw)
    return sanitised if sanitised else "default"


async def _cleanup_stale_counters(
    tmp_dir: pathlib.Path, ttl_seconds: float, skip_path: pathlib.Path
) -> None:
    """Unlink stale ``claude-tool-count-*`` files in *tmp_dir*.

    Runs the glob and unlink calls via :func:`asyncio.to_thread` so they do
    not block the event loop.

    Args:
        tmp_dir: Directory to scan (normally :func:`tempfile.gettempdir`).
        ttl_seconds: Age in seconds beyond which a file is considered stale.
        skip_path: Path to exclude from cleanup (the current session's counter
            file), preventing a race between cleanup and ``_update_counter``.
    """
    now = time.time()

    def _do_cleanup() -> None:
        for path in tmp_dir.glob("claude-tool-count-*"):
            if path == skip_path:
                continue
            try:
                if now - path.stat().st_mtime > ttl_seconds:
                    path.unlink(missing_ok=True)
            except OSError:
                pass

    await asyncio.to_thread(_do_cleanup)


async def main() -> None:
    """Entry point: read stdin, update counter, maybe emit a suggestion."""
    threshold = _get_env_int("COMPACT_THRESHOLD", 50, 1, 10_000)
    repeat_interval = _get_env_int("COMPACT_REPEAT_INTERVAL", 25, 1, 1_000)
    ttl_hours = _get_env_int("COUNTER_TTL_HOURS", 24, 1, 168)
    ttl_seconds = ttl_hours * 3600.0

    # --- Read and parse stdin ---
    raw_bytes: bytes = await asyncio.to_thread(sys.stdin.buffer.read)
    try:
        payload: object = json.loads(raw_bytes)
    except json.JSONDecodeError:
        payload = {}

    session_id_raw: str = ""
    if isinstance(payload, dict):
        session_id_raw = str(payload.get("session_id", ""))
    session_id = _sanitise_session_id(session_id_raw)

    tmp_dir = pathlib.Path(tempfile.gettempdir())
    counter_path = tmp_dir / f"claude-tool-count-{session_id}"

    # Start stale-counter cleanup concurrently.
    cleanup_task = asyncio.create_task(
        _cleanup_stale_counters(tmp_dir, ttl_seconds, counter_path)
    )

    # --- Read, increment, and persist counter (with exclusive lock) ---
    def _update_counter() -> int:
        """Open (or create) the counter file, lock it, update, and return new count."""
        raw_fd = os.open(counter_path, os.O_CREAT | os.O_RDWR, 0o600)
        fd = os.fdopen(raw_fd, "r+b")
        try:
            # LOCK_EX makes the read-modify-write cycle atomic across concurrent
            # hook invocations (e.g. parallel subagent tool calls).
            fcntl.flock(fd, fcntl.LOCK_EX)
            fd.seek(0)
            raw_content = fd.read()
            count = 0
            reset = False
            try:
                count = int(raw_content.strip())
            except ValueError:
                reset = True

            if not reset:
                # mtime reflects the last write. A slow session spanning the TTL boundary
                # will silently reset mid-session — intentional; idle sessions are treated
                # as expired rather than accumulating a stale count indefinitely.
                # Check mtime via the already-open fd to avoid a TOCTOU race.
                mtime = os.fstat(fd.fileno()).st_mtime
                if time.time() - mtime > ttl_seconds:
                    reset = True

            if reset:
                count = 1
            else:
                count += 1

            # seek(0) before truncate is load-bearing: repositions the write pointer
            # so the subsequent write lands at byte 0, not at a stale position.
            fd.seek(0)
            fd.truncate(0)
            fd.write(str(count).encode())
            fd.flush()
            return count
        finally:
            fcntl.flock(fd, fcntl.LOCK_UN)
            fd.close()

    count: int = await asyncio.to_thread(_update_counter)

    # --- Decide whether to emit a suggestion ---
    should_suggest = count >= threshold and (
        count == threshold or (count - threshold) % repeat_interval == 0
    )

    if should_suggest:
        if count == threshold:
            message = (
                f"[StrategicCompact] {count} tool calls"
                " \u2014 good time to /compact before your next phase."
            )
        else:
            message = (
                f"[StrategicCompact] {count} tool calls"
                " \u2014 consider /compact if transitioning phases."
            )

        output = {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "approve",
                "permissionDecisionReason": message,
            }
        }
        sys.stdout.write(json.dumps(output))
        sys.stdout.flush()

    # Wait for the cleanup task before exiting.
    await cleanup_task


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as exc:  # pylint: disable=broad-except
        print(f"strategic_compact error: {exc}", file=sys.stderr)
    sys.exit(0)
