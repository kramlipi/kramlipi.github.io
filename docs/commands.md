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
```

Checks Python, ripgrep, config, and optionally pings the LLM provider.

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
