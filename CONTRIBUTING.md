# Contributing

## Commit message format

[Conventional Commits](https://www.conventionalcommits.org/) are required.
PR titles are validated by the `pr-title` workflow on every push.

| Type | When to use |
|---|---|
| `feat:` | New agent or skill |
| `fix:` | Bug fix to existing agent/skill behaviour |
| `refactor:` | Restructure without behaviour change |
| `docs:` | Documentation, ADRs, comments |
| `chore:` | CI, config, tooling |

Breaking changes: add `!` after the type (`feat!:`) or include a `BREAKING CHANGE:` footer.

## Adding an agent

1. Run `/new-agent <name> — <description>` — the skill scaffolds the `.md` file.
2. Add the agent to the roster table in `.claude/agents/orchestrator.md`, `CLAUDE.md`, and `README.md`.
3. Commit with `feat: add <name> agent`.

## Adding a skill

1. Create `.claude/skills/<name>/SKILL.md` with YAML frontmatter + instructions.
2. Add the skill to the Skills table in `CLAUDE.md`.
3. Commit with `feat: add <name> skill`.

## Adding new versioned items to `.claude/`

If you add a new top-level item under `.claude/` that should be versioned (e.g. `commands/`, `hooks/`):
1. Add a corresponding `ln -sfn` line to the `setup` task in `Taskfile.yml`.
2. Document it in the repo structure section of `CLAUDE.md`.

## Versioning

Versioning is fully automated on merge to `main`. Do not edit `version.txt` or `CHANGELOG.md`
manually — Commitizen manages both.
