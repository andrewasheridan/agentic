# 0003. Commitizen for versioning a non-Python config repository

Date: 2026-03-22
Status: Accepted

## Context

The repo needs semantic versioning driven by conventional commits so that a meaningful version history exists and releases are automated. The repo contains no Python source code, and adopting a language-specific dependency manager would introduce unnecessary complexity.

## Decision

Use [Commitizen](https://commitizen-tools.github.io/commitizen/) configured via `.cz.toml`. Version state is stored in `version.txt` (a plain text file) rather than `pyproject.toml`. In CI, commitizen is installed standalone via `pip install commitizen` — no Python project setup is needed.

## Alternatives Considered

- **standard-version** (Node.js) — works well but introduces a Node/npm dependency for a repo with no JavaScript
- **release-please** (Google) — GitHub Actions–native but opinionated about release PR structure and less flexible for config-only repos
- **Manual tagging** — no automation; easy to forget or apply inconsistently
- **semantic-release** — powerful but Node-based and configuration-heavy

## Consequences

**Positive:**
- Consistent with the Python toolchain already familiar to this project's sole user
- `pip install commitizen` in CI is a single line; no project-level dependency management required
- `version.txt` is human-readable and trivially parseable in shell scripts

**Negative:**
- Commitizen is primarily oriented toward Python projects; some docs and examples assume `pyproject.toml`
