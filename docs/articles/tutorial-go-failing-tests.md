---
title: Fix Failing Go Tests Until go test Passes
description: >-
  Build a broken Add() in a Go module, watch go test fail, then fix it with
  Kramlipi code-agent — and learn why you must never use pytest as verify-cmd.
keywords: >-
  golang go test tutorial, failing unit test, code-agent verify-cmd, go mod,
  Kramlipi AI Code Agent, never pytest on Go
---

# Fix Failing Go Tests Until `go test` Passes

Your microservice PR looked fine in review. Then the build badge flipped red:

```text
--- FAIL: TestAdd (0.00s)
    main_test.go:6: Add(2,3) = -1; want 5
FAIL
```

Someone swapped `+` for `-` in a helper. The fix is one character. The *process* is what burns time: context-switching, re-running tests locally, pushing, waiting on CI again.

**Kramlipi AI Code Agent** automates the boring part — but with a constraint most chatbots ignore. It edits your repo with tools and **only stops when `--verify-cmd` exits 0**. It does not invent success. If `go test` is still failing, the run is not finished.

This tutorial uses a tiny Go module under `/tmp/go-demo`. Copy, paste, watch it work.

---

## What you need

| Item | Notes |
|------|-------|
| Go toolchain | `go version` must work on your machine |
| `code-agent` binary | [GitHub Releases](https://github.com/kramlipi/code-agent-binaries/releases) |
| API key | Gemini, Claude, or OpenAI |

```bash
chmod +x code-agent
export CODE_AGENT_MODEL=gemini/gemini-2.0-flash
export GEMINI_API_KEY=your-key-here
# Or: ANTHROPIC_API_KEY / OPENAI_API_KEY with matching CODE_AGENT_MODEL

./code-agent doctor --provider-test
```

!!! warning "Default mode does not install Go"
    If `go` is missing from PATH, default mode **will not** download or apt-install it for you. That is deliberate — the 0.1 product promise assumes your toolchain is already there. If you need the agent to install missing toolchains on a trusted machine, see [Ultra intelligence mode (cascade)](../features/ultra-intelligence.md).

---

## Step 1 — Create a failing Go test

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

Expected failure:

```text
--- FAIL: TestAdd (0.00s)
    main_test.go:6: Add(2,3) = -1; want 5
FAIL
```

Capture the log for the expert path:

```bash
go test -v ./... 2>&1 | tee /tmp/go-test.log
```

---

## Step 2 — Fix with `code-agent run`

Go projects use **`go test`**, not pytest. Always.

```bash
code-agent run \
  "Fix failing TestAdd in main_test.go. The Add function in main.go has a bug. Run 'go test -v ./...' until all tests pass. Minimal change only." \
  --verify-cmd "go test -v ./..." \
  -w /tmp/go-demo
```

### The proof loop

1. Agent reads `main.go` and `main_test.go`.
2. Agent patches `main.go` via file tools.
3. Agent runs `go test -v ./...` because of `--verify-cmd`.
4. Exit 0 → done. Exit non-zero → retry.

No green `go test`, no “fixed” message. That is the product rule.

On success:

```text
Status: done
Files: main.go
```

Confirm locally:

```bash
cd /tmp/go-demo && go test -v ./...
# PASS
```

### Flags explained

| Flag | Value | Why for Go |
|------|-------|------------|
| `--verify-cmd` | `go test -v ./...` | **Must** be Go's test runner — the same command CI uses |
| `-w` | `/tmp/go-demo` | Module root — the directory containing `go.mod` |

If your CI runs `go test ./...` without `-v`, use that exact string in `--verify-cmd`. Match CI, not your local habit.

---

## Step 3 — Fix with `bug-fix` expert (from CI log)

When GitHub Actions already captured the failure:

```bash
cd /tmp/go-demo
go test -v ./... 2>&1 | tee /tmp/go-test.log

code-agent experts run bug-fix \
  --log /tmp/go-test.log \
  --verify-cmd "go test -v ./..." \
  -w /tmp/go-demo
```

The Go parser catches compiler errors (`main.go:line: undefined`), test failures, and build breaks. But again: **parser hints never override `--verify-cmd`**. The subprocess is the scoreboard.

Optional:

```bash
# Safe first run
code-agent experts run bug-fix ... --dry-run ...

# Open draft PR after local green
code-agent experts run bug-fix ... --publish --base-branch main
```

---

## NEVER use pytest verify on Go

This sounds obvious until someone copy-pastes a Python CI snippet:

```bash
# WRONG — do not do this on a Go repo
code-agent run "fix tests" --verify-cmd "pytest -q" -w /tmp/go-demo
```

What happens:

- The agent tries to run pytest in a Go module.
- There is no `tests/test_*.py`.
- The loop spins, or worse, the model hallucinates progress.

| Language | Correct `--verify-cmd` |
|----------|------------------------|
| Go | `go test ./...` or `go test -v ./...` |
| Python | `pytest -q` |
| Java | `mvn test -q` or `./gradlew test` |

One repo, one verify command, one toolchain.

---

## Real-world layout: agent install ≠ your Go repo

Your `code-agent` binary lives somewhere. Your service lives elsewhere. That is fine:

```bash
# Terminal 1 — your Go service
cd ~/projects/my-go-service
go test -v ./... 2>&1 | tee /tmp/go-ci.log

# Terminal 2 — run the agent
code-agent experts run bug-fix \
  --log /tmp/go-ci.log \
  --verify-cmd "go test -v ./..." \
  -w ~/projects/my-go-service
```

**One `-w`**, pointing at the Go repo with `go.mod`. Never point `-w` at the agent's own install directory.

---

## When Go itself is missing

Default mode classifies “`go: command not found`” as an **environment** problem and stops. It will not `apt install golang` or download a tarball.

On a trusted laptop or VM where you *want* toolchain installation, opt into cascade mode — documented in [Ultra intelligence mode (cascade)](../features/ultra-intelligence.md):

```bash
code-agent run "Make Go unit tests pass. Minimal code changes." \
  --verify-cmd "go test ./..." \
  --autonomy cascade \
  --approve-privileged \
  -w /path/to/go-project
```

For most CI pipelines: install Go in the workflow YAML. Let the agent fix **code**.

---

## Common mistakes

| Mistake | Result | Fix |
|---------|--------|-----|
| `--verify-cmd "pytest -q"` on Go | Wrong runner, wasted loops | Use `go test ./...` |
| `-w` not at `go.mod` root | “go.mod not found” | `-w` = directory with `go.mod` |
| Verify cmd differs from CI | Local green, CI red | Copy CI's exact `go test` line |
| Expecting Go install in default mode | ENV failure, no fix | Pre-install Go, or use [cascade mode](../features/ultra-intelligence.md) |
| Running `go test` outside module | Module errors | `cd` to module root first |

---

## What you learned

- Go proof = `go test`, full stop.
- `-w` must be the module root; `--verify-cmd` must match CI.
- Default mode fixes **code**, not missing toolchains.
- The agent stops only when verify exits 0 — never on model confidence alone.

**Next:** [Quick Start](https://kramlipi.github.io/quick-start/) · [Go examples](../examples/go.md) · [Coverage tutorial](tutorial-raise-coverage.md) · Questions: [cluevion@gmail.com](mailto:cluevion@gmail.com)
