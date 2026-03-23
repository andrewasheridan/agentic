---
description: Audit a proposed new dependency via the dependency-auditor agent
allowed-tools: Agent
---

Audit the package named in $ARGUMENTS using the dependency-auditor agent.

## Steps

1. **Get package name** — Use `$ARGUMENTS` as the package name to audit. If `$ARGUMENTS` is empty, ask: "Which package would you like to audit?"

2. **Identify project context** — Read `CLAUDE.md` to understand the project's language, package manager, and dependency config file (e.g. `pyproject.toml`, `package.json`, `go.mod`).

3. **Delegate to dependency-auditor** — Invoke the `dependency-auditor` agent with:
   - Package to audit: the name from `$ARGUMENTS`
   - Project context: language, package manager, and dependency config file from step 2
   - Strong stdlib preference — external dependencies only if the stdlib alternative is significantly more complex

4. **Report the verdict** — Present the agent's APPROVED or REJECTED decision, its one-paragraph justification, and any suggested alternative if rejected.
