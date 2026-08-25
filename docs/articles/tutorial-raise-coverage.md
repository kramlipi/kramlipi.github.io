---
title: Raise Unit Test Coverage Without Deleting Code
description: >-
  Break an 80% pytest-cov gate on purpose, let Kramlipi code-agent add tests for
  uncovered multiply() — plus brief Go and Java JaCoCo paths.
keywords: >-
  pytest-cov fail-under, raise code coverage, unit test tutorial, code-agent bug-fix,
  go test coverage, jacoco, Kramlipi AI Code Agent
---

# Raise Unit Test Coverage Without Deleting Code

The PR is ready. Code review approved. Then the coverage bot comments:

```text
FAIL Required test coverage of 80% not reached. Total coverage: 62.50%
```

You added `multiply()` last week. You did not add a test. The gate is doing its job — and now merge is blocked over a function that works fine but nobody exercised in CI.

The cynical fix is delete `multiply()` or lower the threshold in `.coveragerc`. The professional fix is write a test. The **fast** professional fix is let **Kramlipi AI Code Agent** write the test — under one hard rule: it edits the repo with tools and **only stops when `--verify-cmd` exits 0**. It does not invent success. It is explicitly instructed to **add tests**, not delete production code to cheat the gate.

This tutorial breaks coverage on a Python demo, raises it with the agent, then sketches Go and Java equivalents.

---

## What you need

| Item | Where |
|------|-------|
| `code-agent` binary | [GitHub Releases](https://github.com/kramlipi/code-agent-binaries/releases) |
| Python + pytest + pytest-cov | `pip install pytest pytest-cov` |
| API key | Gemini, Claude, or OpenAI |

```bash
chmod +x code-agent
export CODE_AGENT_MODEL=gemini/gemini-2.0-flash
export GEMINI_API_KEY=your-key-here

./code-agent doctor --provider-test
```

---

## Step 1 — Start from a passing Python project

If you completed the [Python failing tests tutorial](tutorial-python-failing-tests.md), reuse `/tmp/py-demo`. Otherwise, scaffold quickly:

```bash
mkdir -p /tmp/py-demo && cd /tmp/py-demo
git init
mkdir -p myapp tests

cat > myapp/calc.py <<'EOF'
def add(a: int, b: int) -> int:
    return a + b

def multiply(a: int, b: int) -> int:
    return a * b
EOF

cat > tests/test_calc.py <<'EOF'
from myapp.calc import add

def test_add():
    assert add(2, 3) == 5
EOF

pip install pytest pytest-cov
```

`add()` has a test. `multiply()` does not. That is the gap.

---

## Step 2 — Break the coverage gate on purpose

Run pytest with an 80% fail-under gate:

```bash
cd /tmp/py-demo

pytest -q \
  --cov=myapp \
  --cov-report=term-missing \
  --cov-fail-under=80
```

Expected failure:

```text
FAIL Required test coverage of 80% not reached. Total coverage: 6x.xx%
```

The `term-missing` report shows exactly which lines lack coverage — typically `multiply()` in `myapp/calc.py`.

Save the log:

```bash
pytest -q \
  --cov=myapp \
  --cov-report=term-missing \
  --cov-fail-under=80 \
  2>&1 | tee /tmp/cov.log
```

---

## Step 3 — Let the agent add tests (not delete code)

```bash
code-agent experts run bug-fix \
  --log /tmp/cov.log \
  --verify-cmd "pytest -q --cov=myapp --cov-report=term-missing --cov-fail-under=80" \
  -w /tmp/py-demo
```

Or use prompt mode:

```bash
code-agent run \
  "Increase unit test coverage for myapp to at least 80%. Add tests for uncovered functions like multiply() in myapp/calc.py. Do NOT delete production code or lower the coverage threshold." \
  --verify-cmd "pytest -q --cov=myapp --cov-report=term-missing --cov-fail-under=80" \
  -w /tmp/py-demo
```

### What the agent should do

1. Read the coverage report (missing line numbers).
2. Add tests under `tests/` — e.g. `test_multiply()` asserting `multiply(3, 4) == 12`.
3. Re-run the **full** verify command including `--cov-fail-under=80`.
4. Stop only when exit code = 0.

### What the agent must NOT do

- Delete `multiply()` to bump the percentage.
- Edit CI YAML to remove the gate.
- Claim success while coverage is still below 80%.

The verify subprocess prevents all three.

On success:

```text
Status: done
Files: tests/test_calc.py
```

Confirm:

```bash
cd /tmp/py-demo
pytest -q --cov=myapp --cov-report=term-missing --cov-fail-under=80
# all tests passed, coverage >= 80%
```

### Flags explained

| Flag | Value | Meaning |
|------|-------|---------|
| `--verify-cmd` | Full pytest-cov command **with** `--cov-fail-under=80` | Agent must satisfy the gate, not just run tests |
| `-w` | `/tmp/py-demo` | Repo root |
| `--log` | `/tmp/cov.log` | Coverage failure intake for `bug-fix` |

**Critical:** include the coverage flags inside `--verify-cmd`. If you only pass `pytest -q`, the agent might green tests while coverage stays red.

---

## Step 4 — One-module iteration loop

On large repos, narrow scope while exploring:

```bash
pytest -q tests/test_calc.py \
  --cov=myapp.calc \
  --cov-report=term-missing \
  --cov-fail-under=0
```

Read the `Missing` column — those line numbers need tests. Then widen verify back to the full package gate before calling the job done.

HTML report for human review:

```bash
pytest -q --cov=myapp --cov-report=html
# open htmlcov/index.html
```

---

## Go — brief path

Go coverage gates vary by team. A common pattern:

```bash
cd /path/to/go-module
go test ./... -coverprofile=coverage.out
go tool cover -func=coverage.out
```

If CI fails because a function lacks tests, point the agent at the same proof:

```bash
go test ./... 2>&1 | tee /tmp/go-cov.log

code-agent experts run bug-fix \
  --log /tmp/go-cov.log \
  --verify-cmd "go test ./..." \
  -w /path/to/go-module
```

Use whatever `--verify-cmd` your pipeline runs — including custom scripts that enforce a coverage threshold. The agent adds `_test.go` files; it does not delete exported functions to game metrics.

See [Fix failing Go tests](tutorial-go-failing-tests.md) for module layout and the **never use pytest on Go** rule.

---

## Java — JaCoCo brief path

Maven projects often attach JaCoCo in `pom.xml`. A typical verify line:

```bash
mvn test jacoco:report 2>&1 | tee /tmp/java-cov.log

code-agent experts run bug-fix \
  --log /tmp/java-cov.log \
  --verify-cmd "mvn test jacoco:report" \
  -w /path/to/maven-module
```

Gradle teams use `./gradlew test jacocoTestReport` — swap the verify command accordingly.

The agent adds classes under `src/test/java/` for uncovered methods. Same rule: **add tests, do not delete production code** to pass JaCoCo.

See [Fix failing Java tests](tutorial-java-failing-tests.md) for Maven module layout.

---

## CI babysit when coverage keeps failing

Coverage regressions often appear on PR #N after new code lands without tests:

```bash
code-agent experts watch \
  --pr 17 \
  --verify-cmd "pytest -q --cov=myapp --cov-fail-under=80" \
  -w /path/to/python-repo
```

Each cycle: read failure → add tests → re-run verify → push (if `--publish` is on).

---

## Common mistakes

| Mistake | Result | Fix |
|---------|--------|-----|
| `--verify-cmd "pytest -q"` without cov flags | Tests green, coverage still red | Include full gate: `--cov-fail-under=80` |
| Agent deletes uncovered functions | Fake coverage win | Re-run with explicit “add tests only” prompt; verify catches deletions if tests break |
| Wrong `-w` | Tests added in wrong repo | `-w` = project root where pytest runs |
| Lowering threshold instead of testing | Technical debt | Keep gate in verify-cmd; fix with tests |
| Go/Java verify mismatch | Wrong toolchain | Use `go test ./...` or `mvn test jacoco:report` — not pytest |

---

## What you learned

- Coverage gates belong **inside** `--verify-cmd`, not just in CI YAML.
- The agent adds tests; verify prevents cheater deletes.
- Same pattern extends to Go (`go test ./...`) and Java (JaCoCo via Maven/Gradle).
- Exit code 0 on your gate is the only success signal.

**Next:** [Quick Start](https://kramlipi.github.io/quick-start/) · [Coverage runbook](../features/coverage.md) · [Python](tutorial-python-failing-tests.md) · [Go](tutorial-go-failing-tests.md) · [Java](tutorial-java-failing-tests.md) · Questions: [cluevion@gmail.com](mailto:cluevion@gmail.com)
