---
title: Ultra intelligence mode (cascade)
description: >-
  Opt-in autonomy=cascade with --approve-privileged — nested env subgoals that
  can install missing toolchains (e.g. Go) on a trusted runner, then re-verify.
keywords: cascade, autonomy, approve-privileged, install go, missing toolchain
---

# Ultra intelligence mode (cascade)

**Default mode** (`aal`) fixes **code** against your `--verify-cmd`. It does **not** download Go, Node, or OS packages.

**Ultra intelligence mode** is the opt-in name for `--autonomy cascade` + `--approve-privileged`: when verify fails because the **toolchain is missing**, the agent pushes an env subgoal, runs typed EnvTools (not free shell), installs when allowed, then re-runs the **same** verify command.

Use only on a **trusted runner** (your laptop / approved VM). Do not enable this on untrusted CI by default.

---

## Why default mode skips “install Go”

| Layer | Behavior |
|-------|----------|
| Product promise (0.1) | Toolchain must already be installed |
| Default `aal` | Allowlisted dep installs only (`go mod download`, `pip install -r`, …) — needs `go` on PATH |
| LLM prompts | Forbidden from `apt` / `sudo` / freeform package install |
| Missing `go` | Classified as ENVIRONMENT → fail closed or swap verify — **not** “download Go” |

Cascade is documented in the product design docs; it was kept off the public Quick Start on purpose until now (privilege + promise scope).

---

## Demo: Go missing → install → `go test` green

### 0. Preconditions

- Binary or `pip install` of `code-agent` on the host
- LLM key set (`GEMINI_API_KEY` / Claude / OpenAI — see [Quick Start](../quick-start.md))
- A Go repo under `-w` (even if `go` is **not** installed yet)
- Linux with `apt-get`/`dnf`, or macOS with Homebrew
- Ability to install packages (often needs passwordless `sudo` if `cascade.allow_sudo` is on)

### 1. Prove Go is missing (optional)

```bash
which go || echo "go not on PATH"
go test ./...   # expect: command not found
```

### 2. Dry-run first (no install)

```bash
code-agent run "Make Go unit tests pass. Minimal code changes." \
  --verify-cmd "go test ./..." \
  --autonomy cascade \
  --approve-privileged \
  --dry-run \
  -w /path/to/go-project
```

You should see env frames / would-run install notes — no packages installed.

### 3. Live ultra intelligence run

```bash
export CODE_AGENT_MODEL=gemini/gemini-2.0-flash   # or your model
export GEMINI_API_KEY=…                           # or Claude / OpenAI key

code-agent run "Make Go unit tests pass. Minimal code changes." \
  --verify-cmd "go test ./..." \
  --autonomy cascade \
  --approve-privileged \
  -w /path/to/go-project
```

**What you should see:**

1. Verify fails → `go: command not found` (ENVIRONMENT)
2. Cascade **pushes** an env frame (`ensure_toolchain` / `system_package_install` for `golang`)
3. Install runs (apt/brew) when privileged
4. Stack **pops** → same `go test ./...` re-runs
5. If tests still fail for **code** reasons, the agent edits the repo until verify exits `0`

### 4. Equivalent env vars

```bash
export CODE_AGENT_AUTONOMY=cascade
# still pass --approve-privileged on the CLI (or set cascade.approve_privileged in config)
```

---

## Autonomy cheat sheet

| Mode | Flag | Installs missing Go? | Use when |
|------|------|----------------------|----------|
| Strict | `--autonomy strict` | No | Code-only; no env remedy |
| AAL (default) | `--autonomy aal` | No | CI / normal demos; toolchain already present |
| **Ultra intelligence** | `--autonomy cascade --approve-privileged` | **Yes** (typed EnvTools) | Trusted runner; missing toolchain is the blocker |

---

## Safety

- Without `--approve-privileged`, cascade still **fails closed** on high-privilege installs.
- `--dry-run` never installs.
- Privileged packages can be restricted via `cascade.privileged_packages` in config.
- Prefer default `aal` in customer CI; reserve ultra intelligence for operator-approved hosts.

---

## Related

- [Quick Start](../quick-start.md) · [Troubleshooting](../troubleshooting.md) · [Commands](../commands.md)
