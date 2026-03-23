---
description: Run the project's check suite and report CI-equivalent status
allowed-tools: Bash
---

Run the full check suite and report pass/fail per step.

## Steps

1. **Find the check command** — Read `CLAUDE.md` to find the project's check command. Common patterns:
   - `task check` if a `Taskfile.yml` is present
   - `make check` if a `Makefile` is present
   - The specific commands listed in CLAUDE.md

2. Run the check command.

3. Parse the output and report status for each check that ran:

   | Check | Status |
   |---|---|
   | Lint | ✓ / ✗ |
   | Format | ✓ / ✗ |
   | Type check | ✓ / ✗ |
   | Tests | ✓ / ✗ |
   | (any others) | ✓ / ✗ |

4. For any failing check, show the relevant error lines and suggest the fix command as documented in CLAUDE.md.

5. If all checks pass: report **"All checks passed ✓"**
