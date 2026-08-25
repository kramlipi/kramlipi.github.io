---
title: "Tutorial: Ultra Intelligence When Go Is Missing"
description: >-
  go: command not found blocks default aal mode. Opt into ultra intelligence
  with --autonomy cascade --approve-privileged on a trusted runner — dry-run
  first, then install toolchain and re-verify. 0.1 promise excludes auto install by default.
keywords: >-
  ultra intelligence, cascade, approve-privileged, missing go, toolchain install,
  verify-cmd, trusted runner, Kramlipi code-agent
---

# Ultra Intelligence: When `go` Isn't on PATH

**Kramlipi AI Code Agent** · [kramlipi.github.io](https://kramlipi.github.io) · [Binaries](https://github.com/kramlipi/code-agent-binaries/releases) · cluevion@gmail.com

---

## The pain

Fresh laptop. Minimal CI image. You clone a Go service and run:

```bash
go test ./...
# bash: go: command not found
```

You point **Kramlipi code-agent** at the repo with the honest gate:

```bash
code-agent run "Make unit tests pass." \
  --verify-cmd "go test ./..." \
  -w /path/to/go-project
```

The run stops — not because your handlers are wrong, but because **`go` doesn't exist**. Default **AAL** mode (`--autonomy aal`) treats this as **ENVIRONMENT**, not **CODE**. It will **not** download Go, run `apt install`, or rewrite your app to pretend tests passed.

That is intentional. The **0.1 product promise** says: toolchain on the runner **before** the agent runs. Fail closed beats silent `sudo`.

When the blocker really is a missing compiler — on **your** machine or an **approved** VM — you opt into **ultra intelligence mode**.

Deep reference: **[Ultra intelligence (cascade)](https://kramlipi.github.io/features/ultra-intelligence/)**

---

## Default vs ultra intelligence

| Mode | Flags | Missing `go` on PATH |
|------|-------|----------------------|
| **AAL (default)** | `--autonomy aal` or omit | Diagnose ENVIRONMENT → **no** toolchain download |
| **Strict** | `--autonomy strict` | Code-only; no env remedy at all |
| **Ultra intelligence** | `--autonomy cascade --approve-privileged` | Typed **EnvTools** may install Go (apt/brew), then **same** `go test ./...` re-runs |

Ultra intelligence = **`--autonomy cascade` + `--approve-privileged`**. Nested env subgoals push onto a stack; install runs through allowlisted tools — not freeform shell as root.

**Trusted runner only.** Your laptop, your dev VM, a golden image you control. **Do not** enable cascade on untrusted multi-tenant CI by default.

---

## Preconditions

- `code-agent` installed — [Quick Start](../quick-start.md) or [binaries](https://github.com/kramlipi/code-agent-binaries/releases)
- LLM key set (`GEMINI_API_KEY` / Claude / OpenAI)
- A Go repo under `-w` (tests may fail for code reasons **after** Go exists)
- Linux (`apt`) or macOS (`brew`) with permission to install packages
- Passwordless `sudo` if your config allows `cascade.allow_sudo`

Prove the symptom:

```bash
which go || echo "go not on PATH"
go test ./... 2>&1 | head -3
# expect: command not found
```

---

## Step 1 — Dry-run (see the plan, no install)

Always dry-run cascade on a new machine:

```bash
export GEMINI_API_KEY=your-key

code-agent run "Make Go unit tests pass. Minimal code changes only." \
  --verify-cmd "go test ./..." \
  --autonomy cascade \
  --approve-privileged \
  --dry-run \
  -w /path/to/go-project
```

You should see **env frames** in the trace — notes like `ensure_toolchain` / package install for `golang` — **without** packages actually installed. If dry-run looks wrong, fix config before live.

---

## Step 2 — Live ultra intelligence run

```bash
code-agent run "Make Go unit tests pass. Minimal code changes only." \
  --verify-cmd "go test ./..." \
  --autonomy cascade \
  --approve-privileged \
  -w /path/to/go-project
```

### Expected sequence

1. Verify runs → `go: command not found` → classified **ENVIRONMENT**
2. Cascade **pushes** env subgoal → typed install (e.g. `golang` via apt/brew)
3. Stack **pops** → **same** `--verify-cmd` executes again
4. If tests fail for **code** reasons, agent edits until `go test ./...` exits **`0`**
5. If verify never hits **`0`** → status **`failed`** (fail closed)

**Success is still only verify exit `0`.** Installing Go is a means; green tests are the proof.

Equivalent env vars:

```bash
export CODE_AGENT_AUTONOMY=cascade
# CLI still needs --approve-privileged (or cascade.approve_privileged in config)
```

---

## Why default mode refuses this

Three layers reinforce the same rule:

| Layer | Behavior |
|-------|----------|
| **0.1 promise** | Toolchain must already be present in normal demos and CI |
| **AAL prompts** | Forbidden from `apt` / `sudo` / rewriting app code for `ModuleNotFoundError` |
| **Verify loop** | ENVIRONMENT ≠ CODE — missing command ≠ assertion failure |

So when someone says “the agent didn't fix my Go project,” ask: **was `go` installed?** If not, default mode did the right thing by stopping.

Ultra intelligence is the **escape hatch**, not the default product.

---

## Common mistakes

| Mistake | Fix |
|---------|-----|
| Expecting default mode to install Go | Use cascade + `--approve-privileged` on trusted host |
| Skipping `--dry-run` | See env frames before live install |
| Running cascade on shared CI | Install Go in the **workflow image** instead |
| Wrong verify after install | Keep one gate: `go test ./...` end-to-end |
| `--approve-privileged` on a stranger's runner | **Never** — privilege + install = your trust boundary |
| Confusing install success with task success | Re-run verify yourself; exit **`0`** or it failed |

---

## When **not** to use ultra intelligence

- **Production CI** — bake `go` into the job container (`actions/setup-go`, custom image).
- **Security-sensitive forks** — untrusted code + privileged install = bad combo.
- **“Just fix the assertion”** — if `go test` already runs, stay on default AAL; you're in **CODE** land.

For missing **modules**, default AAL already allowlists `go mod download` — that requires **`go` on PATH**, not a full toolchain install.

---

## The rule, unchanged

Cascade can install tools. It cannot declare victory without **`--verify-cmd` exit `0`**. Model text, installed packages, and green feelings don't count.

That's the same contract as bug-fix and code-review: **fail closed**.

---

## Next steps

- **Full cascade doc:** [Ultra intelligence mode](https://kramlipi.github.io/features/ultra-intelligence/)
- **Normal Go fixes (toolchain present):** [Go example](../examples/go.md) · [Recipes](../recipes.md)
- **Install & keys:** [Quick Start](../quick-start.md)
- **Questions:** cluevion@gmail.com

Try dry-run on a machine without Go. Watch the env frame appear. Then run live once — and don't trust the install until **`go test ./...`** exits **`0`**.
