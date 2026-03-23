# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


### Added

- 11 specialist agents: `code-writer`, `test-writer`, `docstring-writer`, `type-annotator`,
  `reviewer`, `complexity-reducer`, `dead-code-detector`, `dependency-auditor`,
  `changelog-writer`, `adr-writer`, and `orchestrator` as the default router
- 8 skills: `commit`, `new-feature`, `qa`, `release`, `adr`, `audit`, `check`, `new-agent`
- `Taskfile.yml` with `task setup` for granular symlink installation — keeps Claude runtime state outside the repo
- Commitizen versioning via `.cz.toml` and `version.txt`
- GitHub Actions workflows: automated version bump, PR title lint, tag-on-merge

## v0.2.0 (2026-03-23)

### Feat

- initial agent roster, skills, versioning, and ADRs

### Fix

- include official plugin source
