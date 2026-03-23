# 0004. Orchestrator as the sole default agent entry point

Date: 2026-03-22
Status: Accepted

## Context

Claude Code will use tools directly if no default agent is configured, leading to inconsistent behaviour: sometimes delegating to specialist agents, sometimes acting as a generalist, skipping mandatory follow-ups (ADR check, CLAUDE.md update, README update). This variability makes the system unpredictable and error-prone.

## Decision

Set `"agent": "orchestrator"` in `.claude/settings.json`. The orchestrator is the only agent configured as the default entry point. It decomposes every task, selects the appropriate specialist agent, and enforces mandatory follow-up checks after every implementation.

## Alternatives Considered

- **No default agent** — Claude acts as a generalist; specialist agents are invoked ad hoc; mandatory follow-ups are easily forgotten
- **Per-task agent selection by the user** — requires the user to know the roster and remember to invoke the right agent; error-prone

## Consequences

**Positive:**
- Consistent multi-step workflows on every task
- Mandatory follow-ups (ADR, CLAUDE.md, README) are enforced by the orchestrator loop, not by memory
- All tasks go through the same decomposition logic

**Negative:**
- Adds one routing hop to every task, including trivial ones
- The orchestrator itself must be kept up to date when the agent roster changes
