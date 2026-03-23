---
description: Prepare a release — draft changelog entry and suggest version bump
allowed-tools: Agent, Bash
---

Prepare a release by drafting a changelog entry and suggesting the next semantic version.

## Steps

1. **Find commits since last tag** — Run:
   ```
   git log --oneline $(git describe --tags --abbrev=0 2>/dev/null || git rev-list --max-parents=0 HEAD)..HEAD
   ```
   This lists all commits since the last tag (or all commits if no tags exist).

2. **Invoke changelog-writer** — Delegate to the `changelog-writer` agent with:
   - The commit list from step 1
   - Path to existing `CHANGELOG.md` (may not exist yet)
   - Instruction to draft the entry but NOT write it yet — return the draft text

3. **Suggest version bump** — Analyse the commits:
   - Contains `feat!`, `fix!`, or `BREAKING CHANGE` → **major** bump
   - Contains `feat:` (no breaking change) → **minor** bump
   - Only `fix:`, `chore:`, `refactor:`, `perf:`, `docs:`, `test:` → **patch** bump

4. **Find current version** — Check in order: `version.txt`, `pyproject.toml` `[project].version`, latest git tag. Use the first one found.

5. **Show the release plan** — Display:
   - Current version
   - Proposed next version
   - The drafted changelog entry

6. **Wait for confirmation** — Do NOT create tags, bump version files, open PRs, or push anything. Just present the plan. Ask: "Shall I apply the changelog entry to CHANGELOG.md?"
