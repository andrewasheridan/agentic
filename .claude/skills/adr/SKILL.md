---
description: Record an architectural decision via the adr-writer agent
allowed-tools: Agent, Bash
---

Create an Architecture Decision Record for the decision described in $ARGUMENTS.

## Steps

1. **Get decision description** — Use `$ARGUMENTS` as the decision description. If `$ARGUMENTS` is empty, ask: "What architectural decision would you like to record?"

2. **Get today's date** — Run `date +%Y-%m-%d` to get today's date for the ADR.

3. **Find ADR directory** — Look for `docs/decisions/` in the project root. If it does not exist, check CLAUDE.md for the ADR location. If not documented, create `docs/decisions/`.

4. **Delegate to adr-writer** — Invoke the `adr-writer` agent with:
   - Decision to record: the text from `$ARGUMENTS`
   - ADR directory: the path found in step 3
   - Today's date (from step 2)
   - Instruction to check existing ADRs to find the next sequential number

5. **Report** — Tell the user which ADR file was created (e.g. `docs/decisions/0024-use-dagger-for-ci.md`).
