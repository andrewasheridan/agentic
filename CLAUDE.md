# agentic — developer reference

## Project purpose

Versioned, project-agnostic Claude Code configuration: agents, skills, and settings.
Each Claude Code session picks these up via granular symlinks managed by `Taskfile.yml`.

## Repo structure

```
.claude/
  agents/          # One .md file per agent (YAML frontmatter + instructions)
  skills/          # One subdirectory per skill, containing SKILL.md
  settings.json    # Sets orchestrator as the default agent
docs/
  decisions/       # ADRs (NNNN-short-title.md)
.cz.toml           # Commitizen versioning config
version.txt        # Current semver string (managed by Commitizen)
Taskfile.yml        # Task runner (task setup, etc.)
```

## Agent roster

| Agent | Model | Role |
|---|---|---|
| `orchestrator` | sonnet | Default router — decomposes tasks, delegates to specialists |
| `code-writer` | sonnet | Implementation code from a spec |
| `test-writer` | sonnet | pytest test suites |
| `docstring-writer` | haiku | Google-style docstrings |
| `type-annotator` | sonnet | mypy --strict type annotations |
| `reviewer` | sonnet | Advisory code review |
| `complexity-reducer` | haiku | Flag overly complex code |
| `dead-code-detector` | haiku | Find unused/unreachable code |
| `adr-writer` | haiku | Architecture Decision Records |
| `changelog-writer` | haiku | Changelog entries from commits |
| `dependency-auditor` | sonnet | New dependency review |

## Skills

| Skill | File | Trigger |
|---|---|---|
| `commit` | `.claude/skills/commit/SKILL.md` | `/commit` |
| `new-feature` | `.claude/skills/new-feature/SKILL.md` | `/new-feature` |
| `qa` | `.claude/skills/qa/SKILL.md` | `/qa` |
| `release` | `.claude/skills/release/SKILL.md` | `/release` |
| `adr` | `.claude/skills/adr/SKILL.md` | `/adr` |
| `audit` | `.claude/skills/audit/SKILL.md` | `/audit` |
| `check` | `.claude/skills/check/SKILL.md` | `/check` |
| `new-agent` | `.claude/skills/new-agent/SKILL.md` | `/new-agent` |

## Conventions (for code these agents work on)

- **Commits**: [Conventional Commits](https://www.conventionalcommits.org/) — `feat:`, `fix:`, `refactor:`, `docs:`, `chore:`
- **Docstrings**: Google-style, enforced by `docstring-writer`
- **Type annotations**: `mypy --strict`, enforced by `type-annotator`
- **Versioning**: Commitizen semver; state in `version.txt` + `.cz.toml`

## Orchestration flows

- **New feature**: `code-writer → docstring-writer → type-annotator → test-writer → reviewer → (adr-writer if needed)`
- **Architectural decision**: `adr-writer` always (via `/adr` skill)
- **New dependency**: `dependency-auditor` first, then proceed only if approved
- **Release**: `/release` → `changelog-writer`

## Adding an agent

1. Run `/new-agent <name> — <one-line description>` to scaffold the file
2. Add a row to the **Agent roster** table above and to the roster table in `.claude/agents/orchestrator.md`
3. Commit with `feat: add <name> agent`

## Adding a skill

1. Create `.claude/skills/<name>/SKILL.md` with YAML frontmatter + instructions
2. Add a row to the **Skills** table above
3. Commit with `feat: add <name> skill`

## Symlink setup

Run `task setup` after cloning or after adding new versioned items to `.claude/`.
See `Taskfile.yml` for the full list of items that are symlinked.
