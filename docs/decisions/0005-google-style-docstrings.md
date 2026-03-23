# 0005. Google-style docstrings as the enforced project-wide standard

Date: 2026-03-22
Status: Accepted

## Context

The agents in this repo work on Python codebases. The `docstring-writer` agent needs a single, unambiguous docstring format to target. Multiple formats exist (Google, NumPy, Sphinx/reST, PEP 257 minimal) and mixing them within a codebase creates noise and maintenance burden.

## Decision

All Python docstrings written or enforced by these agents use Google style. The `docstring-writer` agent explicitly targets Google format. All agent instructions that mention docstrings reference Google style.

## Alternatives Considered

- **NumPy style** — preferred in scientific/data-science codebases; visually heavier; not the right default for general-purpose Python
- **Sphinx/reST** — verbose and less readable inline; better suited for large library documentation pipelines
- **PEP 257 minimal** — no structure for Args/Returns/Raises; insufficient for complex functions

## Consequences

**Positive:**
- `docstring-writer` has a single unambiguous target; no per-project configuration needed
- Google style is well-supported by IDEs, `pydoc`, and static analysis tools
- Clear expectations for all agents working with Python code

**Negative:**
- Opinionated — projects that use NumPy style will have their docstrings rewritten to Google style when these agents are applied
