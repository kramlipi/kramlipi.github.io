---
title: Python — Failing Unit Tests
description: >-
  Create a failing pytest, fix it with code-agent run and bug-fix expert,
  with every flag explained.
keywords: python pytest, failing unit test, code-agent bug-fix, verify-cmd
---

# Python — Failing Unit Test Example

End-to-end example: **create a failing test → fix with code-agent**.

---

## 1. Create a failing test (in your repo)

```bash
mkdir -p /tmp/py-demo && cd /tmp/py-demo
git init

# Minimal package
mkdir -p myapp tests
cat > myapp/__init__.py <<'EOF'
def add(a: int, b: int) -> int:
    return a + b
EOF

cat > myapp/calc.py <<'EOF'
def add(a: int, b: int) -> int:
    return a - b   # BUG: should be +
EOF

cat > tests/test_calc.py <<'EOF'
from myapp.calc import add

def test_add():
    assert add(2, 3) == 5
EOF

pip install pytest
pytest -q
```

**Expected (failure):**

```text
FAILED tests/test_calc.py::test_add - assert -1 == 5
1 failed
```

**Save the log:**

```bash
pytest -q 2>&1 | tee /tmp/pytest.log
```

---

## 2. Fix with `code-agent run` (prompt mode)

```bash
source /path/to/ai-code-agent/.venv/bin/activate

code-agent run \
  "Fix the failing test in tests/test_calc.py. The add() function in myapp/calc.py is wrong. Run pytest -q until all tests pass. Change only what is needed." \
  --verify-cmd "pytest -q" \
  -w /tmp/py-demo
```

### Flags explained

| Flag | Value | Meaning |
|------|-------|---------|
| `"..."` | task text | What you want — plain English |
| `--verify-cmd` | `pytest -q` | Agent must run this and get exit `0` before finishing |
| `-w` | `/tmp/py-demo` | **Workspace** — only this repo is edited |

**Expected:**

```text
Status: done
Files: myapp/calc.py
```

**Verify yourself:**

```bash
cd /tmp/py-demo && pytest -q
# 1 passed
```

---

## 3. Fix with `bug-fix` expert (CI log mode)

Best when CI already failed and you have a log file.

```bash
cd /tmp/py-demo
pytest -q 2>&1 | tee /tmp/pytest.log

code-agent experts run bug-fix \
  --log /tmp/pytest.log \
  --verify-cmd "pytest -q" \
  -w /tmp/py-demo
```

### Flags explained

| Flag | Meaning | Why use it |
|------|---------|------------|
| `--log` | Path to pytest output | Expert **parses** failures (file, line, assertion) — no guessing |
| `--verify-cmd` | Must match what CI runs | Same proof as GitHub Actions |
| `-w` | Your Python repo | Agent edits `myapp/` and `tests/` here |
| `--dry-run` | (optional) Try without publish | First safe run |
| `--publish` | (optional) Open draft PR | After local verify works |

**Parser support:** pytest failures, coverage failures, Python tracebacks, mypy.

---

## 4. Raise coverage (add missing unit tests)

Break coverage on purpose:

```bash
cat >> myapp/calc.py <<'EOF'

def multiply(a: int, b: int) -> int:
    return a * b
EOF

# No test for multiply yet
pytest -q --cov=myapp --cov-report=term-missing --cov-fail-under=80 2>&1 | tee /tmp/cov.log
```

Fix:

```bash
code-agent experts run bug-fix \
  --log /tmp/cov.log \
  --verify-cmd "pytest -q --cov=myapp --cov-report=term-missing --cov-fail-under=80" \
  -w /tmp/py-demo
```

Agent adds tests in `tests/` — does **not** remove `multiply()` to cheat.

---

## 5. Open a merge request

```bash
cd /tmp/py-demo
git add . && git commit -m "initial"
git remote add origin git@github.com:YOU/py-demo.git
git push -u origin main

pytest -q 2>&1 | tee /tmp/pytest.log

code-agent experts run bug-fix \
  --log /tmp/pytest.log \
  --verify-cmd "pytest -q" \
  -w /tmp/py-demo \
  --publish \
  --base-branch main
```

| Flag | Meaning |
|------|---------|
| `--publish` | Commit fix, push branch, open **draft PR** via `gh` |
| `--base-branch` | PR merges into `main` |

---

## Common mistakes

| Mistake | Fix |
|---------|-----|
| Forgot `-w` | Agent edits wrong directory |
| Wrong `--verify-cmd` | Use exact CI command: `pytest -q` not `python -m pytest` if CI uses `pytest -q` |
| No venv activated | `code-agent: command not found` |
| No `GEMINI_API_KEY` | `doctor` fails — set key first |

[← Back to Quick Start](../quick-start.md)
