# 0006. PreToolUse hook for strategic context compaction suggestions

Date: 2026-03-23
Status: Accepted

## Context

Claude Code sessions accumulate context as tools execute, eventually filling the context window. The platform offers an auto-compact feature that intelligently prunes old messages, but it triggers at fixed context-usage percentages and may fire mid-task, interrupting work flow.

The Claude Code hook system allows scripts to run as subprocesses on tool events. This decision introduces the first hook in the repository: a `PreToolUse` hook that monitors tool-call frequency and suggests manual compaction at strategic points (e.g., between logical tasks or milestones). This establishes the hooks pattern for the project.

## Decision

Implement a Python 3.14 async `PreToolUse` hook (`strategic_compact.py`) that:

- Tracks tool-call count per session via a file-based counter in the OS temp directory
- Uses `fcntl.LOCK_EX` for exclusive file locking (to prevent race conditions across concurrent hooks)
- Emits advisory `/compact` suggestions via Claude Code's stdout JSON protocol at configurable thresholds
- Always exits with code 0 — never blocks a tool call, ensuring the hook cannot disrupt work
- Cleans up stale counter files in a background asyncio task using a TTL (time-to-live) based on file mtime
- Accepts configuration via environment variables: `COMPACT_THRESHOLD` (default 50), `COMPACT_REPEAT_INTERVAL` (default 25), `COUNTER_TTL_HOURS` (default 24)
- Stores the hook in `.claude/hooks/pretooluse/strategic_compact.py` and is symlinked by `task setup`

## Alternatives Considered

1. **Keep the Node.js version** — A Node.js hook existed; rejected because it adds an unnecessary runtime dependency, contains unfixed race conditions around file access, and does not use the hook output protocol to emit structured suggestions.

2. **Daemon or shared-memory approach** — A long-running daemon could maintain in-memory counters; rejected because it adds operational complexity, requires user setup, and is overkill for a simple counter. A file-based approach is simpler and works across all environments.

3. **Auto-compact only** — Rather than suggesting compaction, automatically trigger it via the hook; rejected because auto-compact fires at arbitrary context-usage percentages (e.g., 75%) and often interrupts work mid-task. User-driven suggestions at logical boundaries preserve cognitive continuity.

4. **Blocking hook (exit code 2)** — Force compaction by exiting non-zero, which prevents the tool call; rejected because this is too aggressive and removes user agency. The decision to compact should remain with the user.

## Consequences

**Positive:**
- Suggests compaction at strategic moments, preserving work flow within logical phases
- File-based counter works across all environments with minimal overhead
- Advisory suggestions respect user autonomy — the user is never blocked
- Configuration via env vars allows per-session tuning without code changes
- Non-blocking hook ensures no degradation to tool-execution performance

**Negative:**
- Every tool call in every session incurs a small file I/O cost (negligible in practice — file lookups and single-byte updates are fast)
- Hook uses `fcntl` for locking, which is POSIX-only; documented as macOS-only for now (Windows support would require `msvcrt` shims)
- Session counter resets are TTL-based (file mtime), not session-start-based — a very long session that spans the TTL boundary will silently reset mid-session (acceptable trade-off; rare in practice)
- Counter filenames encode the session ID, so file permissions are `0o600` (owner-only) to protect against information leakage via temp directory inspection
- Introduces versioning responsibility for the `.claude/hooks/` directory; must be kept in sync across clones via `task setup`
