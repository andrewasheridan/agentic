# 0002. Markdown-per-agent file architecture

Date: 2026-03-22
Status: Accepted

## Context

Claude Code agents and skills must be defined somewhere. The format must be readable by the Claude Code runtime and maintainable over time. Each agent and skill needs clear ownership and a clear history of changes.

## Decision

Each agent lives in its own `.md` file under `.claude/agents/` with a YAML frontmatter block (`name`, `description`, `model`, `tools`) followed by prose instructions. Each skill lives in its own subdirectory under `.claude/skills/` as `SKILL.md`. This is the native Claude Code format.

## Alternatives Considered

- **Single monolithic config file** — harder to diff, review, and maintain; no per-agent git history
- **JSON/YAML config** — loses the ability to write rich prose instructions naturally; not the native format
- **Programmatic generation** — unnecessary complexity for a config repo maintained by one person

## Consequences

**Positive:**
- Each agent has its own git history, making regressions easy to bisect
- PRs and diffs are scoped to the agent being changed
- New agents can be added by dropping a single file; no central registry to update (beyond the orchestrator roster table)

**Negative:**
- No schema validation; a malformed frontmatter block fails silently until Claude Code tries to load it
