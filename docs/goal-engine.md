---
title: Generic Goal-Seeking Engine
description: >-
  How code-agent discovers a SuccessSpec, runs your verify command, and fails
  closed on exit code — Phase A sample commands for Python and Go.
keywords: SuccessSpec, verify-cmd, goal engine, go test, pytest, code-agent
---

# Generic Goal-Seeking Engine

**Product:** [kramlipi code-agent](https://kramlipi.github.io)  
**Contact:** cluevion@gmail.com

code-agent turns a natural-language goal into a closed loop:

1. **Discover** a **SuccessSpec** (how we know we won — usually a shell command)  
2. **Act** with tools (`read_file` / `write_file` / `ast_edit`)  
3. **Gate** on a real subprocess exit code (`--verify-cmd` / auto-discovered verify)

No unrestricted Bash. Workflow YAML stays off-limits. Ambiguous success → fail closed.

| Phase | Status |
|-------|--------|
| **A** — SuccessSpec naming + discovery (this page) | Available on branch `design/generic-goal-engine` |
| **B** — Allowlisted `run_command` + Observation buffer | Planned |
| **C** — UI shows discovery candidates | Planned |

---

## Sample commands

### Inspect discovery (no LLM)

```bash
code-agent doctor --verify-plan "fix failing unit tests" -w .
code-agent doctor --verify-plan "increase coverage to 80%" -w .
code-agent doctor --verify-plan "go test the package" -w /path/to/go-project
```

### Explicit SuccessSpec (recommended)

```bash
export CODE_AGENT_MODEL=gemini/gemini-3.1-flash-lite
export GEMINI_API_KEY="your-key"

# Python
code-agent run "Fix failing unit tests. Minimal changes." \
  --verify-cmd "python3 -m pytest -q" \
  -w /path/to/python-project

# Go
code-agent run "Make unit tests pass. Minimal changes." \
  --verify-cmd "go test ./..." \
  -w /path/to/go-package
```

### Auto-discovered SuccessSpec

```bash
code-agent run "Fix the failing tests" -w /path/to/project
```

Discovery priority: **explicit** → config → CI extract → manifests (`pytest` / `go test` / npm / …).

### Dry-run

```bash
code-agent run "Fix failing tests" \
  --verify-cmd "python3 -m pytest -q" \
  --dry-run \
  -w /path/to/project
```

---

## What “done” means

The verifier re-runs `SuccessSpec.success_cmd` (same as `verify_cmd`).  
**Exit code 0** is required. The LLM cannot override a failed verify.

---

## Related

- [Commands](commands.md) — full CLI flags  
- [Examples — Python](examples/python.md) · [Go](examples/go.md)  
- [Quick Start](quick-start.md)
