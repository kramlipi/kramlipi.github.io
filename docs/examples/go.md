---
title: Go — Failing Unit Tests
description: >-
  Create a failing go test, fix with code-agent using go test verify-cmd and
  bug-fix expert with flags explained.
keywords: golang go test, failing unit test, code-agent bug-fix
---

# Go — Failing Unit Test Example

Go projects use **`go test`**, not `pytest`. Always set `--verify-cmd "go test ..."`.

---

## 1. Create a failing test

```bash
mkdir -p /tmp/go-demo && cd /tmp/go-demo
git init
go mod init example.com/demo

cat > main.go <<'EOF'
package main

func Add(a, b int) int {
	return a - b // BUG: should be +
}
EOF

cat > main_test.go <<'EOF'
package main

import "testing"

func TestAdd(t *testing.T) {
	if got := Add(2, 3); got != 5 {
		t.Errorf("Add(2,3) = %d; want 5", got)
	}
}
EOF

go test -v ./...
```

**Expected (failure):**

```text
--- FAIL: TestAdd (0.00s)
    main_test.go:6: Add(2,3) = -1; want 5
FAIL
```

**Save log:**

```bash
go test -v ./... 2>&1 | tee /tmp/go-test.log
```

---

## 2. Fix with `code-agent run`

```bash
source /path/to/ai-code-agent/.venv/bin/activate

code-agent run \
  "Fix failing TestAdd in main_test.go. The Add function in main.go has a bug. Run 'go test -v ./...' until all tests pass. Minimal change only." \
  --verify-cmd "go test -v ./..." \
  -w /tmp/go-demo
```

### Flags explained

| Flag | Why for Go |
|------|------------|
| `--verify-cmd "go test -v ./..."` | **Must** be Go's test runner — never `pytest` |
| `-w /tmp/go-demo` | Module root (where `go.mod` lives) |

**Expected:**

```text
Status: done
Files: main.go
```

```bash
cd /tmp/go-demo && go test -v ./...
# PASS
```

---

## 3. Fix with `bug-fix` expert (from log)

```bash
cd /tmp/go-demo
go test -v ./... 2>&1 | tee /tmp/go-test.log

code-agent experts run bug-fix \
  --log /tmp/go-test.log \
  --verify-cmd "go test -v ./..." \
  -w /tmp/go-demo
```

### Flags explained

| Flag | Meaning |
|------|---------|
| `--log /tmp/go-test.log` | Go compiler/test errors parsed automatically |
| `--verify-cmd` | Same command CI uses |
| `-w` | Go module root |
| `--dry-run` | Test locally first, no MR |
| `--publish` | Push fix branch + draft PR |

**Go parser catches:** `main.go:line: undefined`, test failures, build errors.

---

## 4. Fix tests in another repo (real world)

`code-agent` install lives in one folder; **your Go app** in another:

```bash
# Terminal 1 — your Go project
cd ~/karm/my-go-service
go test -v ./... 2>&1 | tee /tmp/go-ci.log

# Terminal 2 — run agent
source ~/karm/ai-code-agent/.venv/bin/activate

code-agent experts run bug-fix \
  --log /tmp/go-ci.log \
  --verify-cmd "go test -v ./..." \
  -w ~/karm/my-go-service
```

!!! warning
    **One** `-w` pointing at the Go repo. Do not point `-w` at `ai-code-agent`.

---

## 5. CI babysit (PR keeps failing)

```bash
code-agent experts watch \
  --pr 42 \
  --verify-cmd "go test -v ./..." \
  -w ~/karm/my-go-service
```

| Flag | Meaning |
|------|---------|
| `--pr 42` | Watch GitHub PR #42 checks |
| `--verify-cmd` | Re-run after each fix attempt |
| `--publish` / `--no-publish` | Push fixes to PR branch (default: publish on) |

---

## Common mistakes

| Mistake | Result |
|---------|--------|
| `--verify-cmd "pytest -q"` on Go repo | Agent runs wrong tool — fails |
| `-w` not at `go.mod` root | Cannot find package |
| Running `go test` outside module | "go.mod not found" |

[← Back to Quick Start](../quick-start.md)
