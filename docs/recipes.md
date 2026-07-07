---
title: Recipe Book
description: >-
  Copy-paste code-agent recipes for Python tests, Go tests, CI logs, coverage
  gates, PR babysitting, and external repositories.
keywords: code-agent recipes, fix pytest, fix go test, bug-fix log, experts watch
---

# Recipe Book

Copy-paste commands for common tasks. Replace paths with your project.

---

## A. Fix Python unit tests

```bash
cd ~/karm/ai-code-agent
source .venv/bin/activate

# See failures first
pytest -q

# Option 1: direct run
code-agent run \
  "Fix all failing unit tests in tests/. Run pytest -q after each change until every test passes. Only change test and source code needed for failures — no refactors." \
  --verify-cmd "pytest -q" \
  -w .

# Option 2: bug-fix expert from log
pytest -q 2>&1 | tee /tmp/pytest.log
code-agent experts run bug-fix \
  --log /tmp/pytest.log \
  --verify-cmd "pytest -q" \
  -w .
```

---

## B. Fix Go tests (external repo)

```bash
# See failures
cd /path/to/your-go-project && go test -v ./...

# Option 1: direct run
code-agent run \
  "Fix all failing Go unit tests. Run 'go test -v ./...' after each change until every test passes." \
  --verify-cmd "go test -v ./..." \
  -w /path/to/your-go-project

# Option 2: bug-fix expert
cd /path/to/your-go-project
go test -v ./... 2>&1 | tee /tmp/go-test.log

code-agent experts run bug-fix \
  --log /tmp/go-test.log \
  --verify-cmd "go test -v ./..." \
  -w /path/to/your-go-project
```

!!! warning "Common mistakes"
    - Do **not** use `pytest` for Go projects
    - Use **one** `-w` pointing at the Go repo root

---

## C. Raise code coverage (Python)

```bash
pytest -q --cov=code_agent --cov-report=term-missing --cov-fail-under=80 \
  2>&1 | tee /tmp/coverage-fail.log

code-agent experts run bug-fix \
  --log /tmp/coverage-fail.log \
  --verify-cmd "pytest -q --cov=code_agent --cov-report=term-missing --cov-fail-under=80"
```

See [Coverage](coverage.md) for the full runbook.

---

## D. Run only impacted tests (PR CI)

```bash
code-agent experts run test-intel --base-branch main
# Run the printed verify_cmd in CI
```

---

## E. Babysit a PR until CI green

```bash
code-agent experts watch --pr 42 --verify-cmd "pytest -q"
```

---

## F. Fix from GitHub Actions run

```bash
code-agent experts run bug-fix \
  --run-id 123456789 \
  --verify-cmd "pytest -q" \
  --publish
```

Requires `gh` authenticated and repo access.

---

## G. SRE alert → fix

```bash
code-agent experts run sre-expert \
  --log /path/to/alert.json \
  --verify-cmd "curl -sf http://localhost:8080/health" \
  --dry-run
```

---

## H. Monitoring audit

```bash
code-agent experts run monitoring-expert --dry-run
```

---

## I. Dry run (no writes)

```bash
code-agent run "Refactor error handling" --dry-run -w .
code-agent experts run bug-fix --log /tmp/ci.log --dry-run
```

---

## J. Interactive chat on a project

```bash
code-agent chat -w /path/to/project
# type tasks; exit with: exit

code-agent chat --resume SESSION_ID -w /path/to/project
```

---

## Prompt templates

**Minimal fix:**

```text
Fix the failing tests. Run VERIFY_CMD after each change. Minimal diff only.
```

**Add feature + test:**

```text
Add FEATURE. Add a test. Match existing code style. Run VERIFY_CMD until green.
```

**Coverage:**

```text
Raise line coverage to THRESHOLD%. Add unit tests under tests/ for uncovered lines.
Do not delete production code. Do not edit .github/workflows.
```
