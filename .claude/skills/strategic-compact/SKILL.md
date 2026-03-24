---
name: strategic-compact
description: Quick reference for deciding when to /compact — decision table, what survives, and hook env vars.
allowed-tools: []
---

# Strategic Compact — Decision Guide

The `strategic_compact.py` hook suggests `/compact` automatically at tool-call thresholds.
Use this skill when you want to reason manually about whether now is a good time.

## When to Compact

| Phase transition | Compact? | Why |
|---|---|---|
| Research → Planning | Yes | Research context is bulky; the plan is the distilled output |
| Planning → Implementation | Yes | Plan lives in files/todos; free up context for code |
| Implementation → Testing | Maybe | Keep if tests reference recent code; compact if switching focus |
| Debugging → Next feature | Yes | Debug traces pollute context for unrelated work |
| Mid-implementation | No | Losing variable names, file paths, and partial state is costly |
| After a failed approach | Yes | Clear dead-end reasoning before trying a new approach |

## What Survives Compaction

| Persists | Lost |
|---|---|
| CLAUDE.md instructions | Intermediate reasoning and analysis |
| TodoWrite task list | File contents you previously read |
| Files on disk | Multi-step conversation context |
| Git state (commits, branches) | Tool call history and counts |

## How to Compact with Context

Pass a summary so Claude knows what to focus on next:

```
/compact Focus on implementing the auth middleware next
```

## Hook Env Vars

Configure `strategic_compact.py` via environment variables in `settings.json` → `env`:

| Var | Default | Effect |
|---|---|---|
| `COMPACT_THRESHOLD` | `50` | Tool calls before first suggestion |
| `COMPACT_REPEAT_INTERVAL` | `25` | Calls between repeat suggestions after threshold |
| `COUNTER_TTL_HOURS` | `24` | Hours before a session counter is considered stale |

To disable the hook, remove its entry from `settings.json` → `hooks.PreToolUse`.
