# 0001. Granular symlink-based dotfiles management

Date: 2026-03-22
Status: Accepted

## Context

The repo needs its `.claude/` contents (agents, skills, settings) to be available at `~/.claude/` so every Claude Code session picks them up. A naive single whole-directory symlink would work but causes Claude's runtime state (worktrees, temporary files, etc.) to be written inside the repo directory — even though `.gitignore` excludes them, they physically live in the repo, creating noise and maintenance friction.

## Decision

Use a `Taskfile.yml` (`task setup`) that creates `~/.claude/` as a real directory and symlinks each versioned item individually: `~/.claude/agents`, `~/.claude/skills`, and `~/.claude/settings.json` each point into the repo. Runtime state at `~/.claude/` stays outside the repo entirely.

## Alternatives Considered

- **Single whole-directory symlink** — simpler but pollutes the repo with runtime state
- **GNU Stow** — purpose-built for this pattern but adds an external dependency; the manual approach is three `ln` commands and equally transparent
- **chezmoi** — powerful but heavyweight for a single-directory config; templating and encryption are unnecessary here
- **Direct copy with a sync script** — breaks the live-edit workflow; changes to agents require an explicit sync step

## Consequences

**Positive:**
- Repo stays clean; `git status` never shows Claude runtime noise
- New machine setup is one command
- Idempotent — `task setup` is safe to re-run after pulling changes

**Negative:**
- Adding a new top-level versioned item to `.claude/` requires a matching `ln` line in `Taskfile.yml`; this is easy to forget
