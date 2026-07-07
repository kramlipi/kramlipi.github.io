---
title: Unit Tests & Coverage
description: >-
  Raise code-agent line coverage with pytest-cov — measure gaps, write tests,
  enforce fail-under gate, and use bug-fix expert for coverage CI failures.
keywords: pytest-cov, code coverage, fail-under, unit tests, bug-fix coverage
---

# Unit Tests & Coverage

Runbook for raising line coverage on Python projects (especially `code_agent`).

## Baseline commands

```bash
pip install -e ".[dev]"

# All tests
pytest -q

# Coverage report with missing lines
pytest -q --cov=code_agent --cov-report=term-missing

# PR gate (fails if below 80%)
pytest -q --cov=code_agent --cov-report=term-missing --cov-fail-under=80
```

**Expected when below gate:**

```text
FAIL Required test coverage of 80% not reached. Total coverage: 68.xx%
```

Exit code: `1`

## HTML report

```bash
pytest -q --cov=code_agent --cov-report=html
# open htmlcov/index.html
```

## One-module loop (fast iteration)

```bash
pytest -q tests/test_tools_files.py \
  --cov=code_agent.tools.files \
  --cov-report=term-missing \
  --cov-fail-under=0
```

Read the `Missing` column — those line numbers need tests.

## Agent-assisted coverage fix

```bash
pytest -q --cov=code_agent --cov-report=term-missing --cov-fail-under=80 \
  2>&1 | tee /tmp/coverage-fail.log

code-agent experts run bug-fix \
  --log /tmp/coverage-fail.log \
  --verify-cmd "pytest -q --cov=code_agent --cov-report=term-missing --cov-fail-under=80"
```

The agent is instructed to **add tests**, not delete production code or edit CI YAML.

## Test conventions

| Rule | Detail |
|------|--------|
| Location | `tests/test_<module>.py` |
| Style | Plain pytest; `tmp_path` for filesystem |
| External I/O | Mock subprocess, network, LLM |
| Assertions | Behavior over implementation |

## Priority backlog (code_agent)

| Priority | Module | Suggested test file |
|----------|--------|---------------------|
| P0 | `tools/git_utils.py` | `tests/test_git_utils.py` |
| P0 | `rag.py` | `tests/test_rag.py` |
| P1 | `publish/git_ops.py` | `tests/test_publish_git_ops.py` |
| P1 | `publish/mr_creator.py` | `tests/test_publish_mr_creator.py` |
| P2 | `cli.py` | `tests/test_cli_*.py` (Typer CliRunner) |

## Anti-patterns

- Deleting hard-to-test code to raise %
- Lowering `fail-under` in CI without team agreement
- Committing `htmlcov/`, `.coverage`, `coverage.json`

## Definition of done

1. `pytest -q` exits `0`
2. `--cov-fail-under=80` exits `0` (or agreed threshold)
3. New tests under `tests/`
4. No `.github/workflows/**` changes
