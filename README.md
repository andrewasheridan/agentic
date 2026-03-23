# agentic

Versioned Claude agents, skills, and settings — project-agnostic dotfiles for Claude Code.

## Setup

Clone the repo, then run `task setup` to symlink versioned items into `~/.claude`:

```bash
git clone https://github.com/andrewjudd/agentic ~/Projects/agentic
cd ~/Projects/agentic
task setup
```

Requires [Task](https://taskfile.dev/) (`brew install go-task`).

`~/.claude/` stays a real directory so Claude runtime state (worktrees, etc.) never
enters the repo. The task is idempotent — safe to re-run after pulling changes.

## What's included

| Path | Contents |
|---|---|
| `.claude/agents/` | 10 specialist agents + orchestrator |
| `.claude/skills/` | 8 skills (slash commands) |
| `.claude/settings.json` | Sets `orchestrator` as the default agent |
| `docs/decisions/` | Architecture Decision Records |

## Agents

| Agent | Role |
|---|---|
| `orchestrator` | Default router — decomposes tasks and delegates to specialists |
| `code-writer` | Writes implementation code from a spec |
| `test-writer` | Writes pytest tests |
| `docstring-writer` | Adds/fixes Google-style docstrings |
| `type-annotator` | Adds/fixes mypy --strict annotations |
| `reviewer` | Advisory code review |
| `complexity-reducer` | Flags overly complex code |
| `dead-code-detector` | Finds unused/unreachable code |
| `adr-writer` | Writes Architecture Decision Records |
| `changelog-writer` | Drafts changelog entries from commits |
| `dependency-auditor` | Reviews proposed new dependencies |

## Skills (slash commands)

| Skill | What it does |
|---|---|
| `/commit` | Run checks, draft conventional commit message, and commit |
| `/new-feature` | Full pipeline: code → docs → types → tests → review |
| `/qa` | Quality sweep: complexity, dead code, code review |
| `/release` | Draft changelog entry and suggest version bump |
| `/adr` | Record an architectural decision |
| `/audit` | Audit a proposed new dependency |
| `/check` | Run CI-equivalent checks and report status |
| `/new-agent` | Scaffold a new agent file |

## Versioning

Versions follow [Semantic Versioning](https://semver.org/) and are managed by
[Commitizen](https://commitizen-tools.github.io/commitizen/).

On every merge to `main` the bump workflow automatically:
1. Runs `cz bump` to determine the next version from conventional commits
2. Opens a version-bump PR (title: `bump: X.Y.Z`)
3. Auto-merges it via squash
4. Creates an annotated git tag `vX.Y.Z`

Requires a `RELEASE_TOKEN` secret — a PAT with `repo` scope — set in the repository settings.

## Commit conventions

Follow [Conventional Commits](https://www.conventionalcommits.org/):

| Type | When to use |
|---|---|
| `feat:` | New agent or skill |
| `fix:` | Bug fix to an existing agent or skill |
| `refactor:` | Restructuring without behaviour change |
| `docs:` | Documentation only |
| `chore:` | CI, config, maintenance |
