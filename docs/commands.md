---
title: CLI Commands
description: >-
  Complete code-agent CLI reference — run, chat, doctor, config, env, and
  experts subcommands with flags and expected output.
keywords: code-agent cli, run, chat, doctor, experts run, verify-cmd
---

# CLI Commands

Quick reference for every `code-agent` command. For copy-paste workflows see [Recipes](recipes.md).

## Global

```bash
code-agent --help
code-agent --version
```

| Flag | Effect |
|------|--------|
| `--config`, `-c` | Path to `config.yaml` |
| `--workspace`, `-w` | Repo root (default: `.`) |

---

## `code-agent run` — one-shot task

Fix, add, or refactor code from a natural-language task.

```bash
code-agent run "TASK" [OPTIONS]
```

| Flag | Effect |
|------|--------|
| `--verify-cmd` | Shell command that must exit `0` |
| `--dry-run` | Plan only; block file writes |
| `--session-id` | Attach to existing session |

**Examples:**

```bash
code-agent run "Add type hints to src/utils.py" -w .
code-agent run "Fix failing login test" --verify-cmd "pytest -q tests/test_auth.py"
code-agent run "Refactor cache module" --dry-run
```

**Success output (shape):**

```text
┌─ Result ─────────────────────────┐
│ Status: done                     │
│ Session: abc123def456            │
│ Run ID: a1b2c3d4e5f6            │
│ Files: src/utils.py              │
└──────────────────────────────────┘
```

---

## `code-agent chat` — interactive REPL

```bash
code-agent chat [-w PATH] [--resume SESSION_ID]
```

Type tasks at `you>` prompt. Type `exit` to quit.

---

## `code-agent doctor` — preflight

```bash
code-agent doctor
code-agent doctor --provider-test
code-agent doctor --verify-plan "fix failing unit tests" -w .
```

Checks Python, ripgrep, config, and optionally pings the LLM provider.

| Flag | Effect |
|------|--------|
| `--provider-test` | Minimal LLM call to validate API key / model |
| `--verify-plan TASK` | Show auto-resolved **SuccessSpec** / verify command for a task (no agent run) |
| `--workspace`, `-w` | Project root for discovery |

**Verify gate:** pass `--verify-cmd` so the agent only finishes when that command exits `0`. See [How to use verify commands](#how-to-use-verify-commands) below.

---

## How to use verify commands

Tell **code-agent** what “done” means with `--verify-cmd`. It edits your repo with tools, then re-runs that command until it exits **0** (or it fails closed).

### See which verify command would be used

No LLM call — discovery only:

```bash
code-agent doctor --verify-plan "fix failing unit tests" -w .
code-agent doctor --verify-plan "increase coverage to 80%" -w .
code-agent doctor --verify-plan "go test the package" -w /path/to/go-project
```

### Fix failing tests (Python)

```bash
cd /path/to/your-python-repo

python3 -m pytest -q   # optional: show red first

code-agent run "Fix all failing unit tests. Minimal changes only — do not change tests unless required." \
  --verify-cmd "python3 -m pytest -q" \
  -w .

python3 -m pytest -q   # same command proves green
```

Narrow the gate:

```bash
code-agent run "Fix the auth tests." \
  --verify-cmd "python3 -m pytest -q tests/test_auth.py" \
  -w .
```

### Fix failing tests (Go)

```bash
cd /path/to/your-go-package

go test ./...

code-agent run "Make unit tests pass. Minimal changes only." \
  --verify-cmd "go test ./..." \
  -w .

go test ./...
```

### Omit `--verify-cmd` (auto-discovery)

If you omit `--verify-cmd`, it tries config → CI → project manifests (`pytest`, `go test`, npm, …). Prefer an **explicit** `--verify-cmd` when you know the right command.

### Docker one-liner

```bash
cd /path/to/your-repo

docker run --rm -it \
  -e GEMINI_API_KEY \
  -e CODE_AGENT_MODEL \
  -v "$PWD:/workspace" \
  ghcr.io/kramlipi/code-agent:latest \
  run "Fix all failing unit tests. Minimal changes only." \
  --verify-cmd "python3 -m pytest -q" \
  -w /workspace
```

For Go, use `--verify-cmd "go test ./..."` (image must have Go, or run the binary locally).

| Tip | Why |
|-----|-----|
| Same verify before and after | Proves the agent actually fixed the failure |
| Keep the prompt tight | “Minimal changes”, “do not weaken other tests” |
| If the run fails | Improve the **prompt**, re-run `code-agent` — don’t hand-edit the fix |
| CI log → fix | `code-agent experts run bug-fix --log fail.log --verify-cmd "…"` |

---

## `code-agent config`

```bash
code-agent config show
```

Prints resolved settings (secrets redacted).

---

## `code-agent env`

```bash
code-agent env sync     # sync keys from host (e.g. Windows geminikey)
code-agent env show     # list discovered keys (redacted)
```

---

## `code-agent experts`

### List experts

```bash
code-agent experts list
```

### Run an expert

```bash
code-agent experts run EXPERT_ID [OPTIONS]
```

| Flag | Effect |
|------|--------|
| `--log FILE` | CI log, alert JSON, or metrics JSON |
| `--run-id ID` | GitHub Actions run id (`bug-fix` only) |
| `--verify-cmd` | Override verification command |
| `--dry-run` | No git publish |
| `--publish` | Commit, push, open draft MR |
| `--approve-publish` | Bypass approval gate |
| `--no-artifacts` | Skip `.code-agent/runs/` |
| `--base-branch` | MR target (default: `main`) |
| `-w`, `--workspace` | Repo root |

### Babysit a PR

```bash
code-agent experts watch --pr NUMBER --verify-cmd "pytest -q"
```

Polls CI on an open PR and runs `bug-fix` when checks fail.

### HTTP serve (platform)

```bash
code-agent experts serve --host 0.0.0.0 --port 8080
```

Webhook router for deploy-guard, budget/throttle, approval gate.

---

## Configuration files

| File | Role |
|------|------|
| `config.yaml` | Model, workspace, expert settings |
| `.env` | API keys (from `env sync`; do not commit) |
| `config.example.yaml` | Template with all options |

**Key settings:**

```yaml
model: gemini/gemini-2.0-flash
workspace: .
max_iterations: 10
temperature: 0.2
```

LiteLLM model strings: `gemini/`, `openai/`, `anthropic/`, `ollama_chat/`, etc.

---

## Outputs

| Location | Contents |
|----------|----------|
| Modified files | In workspace (source/tests) |
| `.code-agent/sessions/` | Chat / run session state |
| `.code-agent/runs/<run_id>/` | Expert artifacts (signals, RCA, trace, diff) |
| Draft MR URL | When `--publish` succeeds |

---

## Related

- [Experts](experts.md) — per-expert inputs and outputs
- [Troubleshooting](troubleshooting.md) — exit codes and common failures
