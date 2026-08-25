---
title: "Tutorial: Fix a Failed CI Log Until verify-cmd Is Green"
description: >-
  Save a red GitHub Actions or local test log, run the bug-fix expert with
  --verify-cmd, and only accept success when your gate exits 0. Parsers for
  pytest, Go, and generic failures — plus ENVIRONMENT vs CODE.
keywords: >-
  bug-fix expert, CI log, verify-cmd, gh run view, pytest parser, go test,
  fail closed, draft PR, Kramlipi code-agent
---

# Fix a Failed CI Log Until Your Tests Pass

**Kramlipi AI Code Agent** · [kramlipi.github.io](https://kramlipi.github.io) · [Binaries](https://github.com/kramlipi/code-agent-binaries/releases) · cluevion@gmail.com

---

## The pain

You wake up to a red check. Slack has a link. The log is four thousand lines of noise — matrix jobs, cache restores, and somewhere near the bottom:

```text
FAILED tests/test_auth.py::test_login_expired - AssertionError: expected 401 got 403
```

You could scroll until your eyes glaze over. You could paste the log into a chatbot and get a confident paragraph that **sounds** fixed. You could hand-edit three files and push, then wait another twenty minutes for CI to tell you it was wrong.

**Kramlipi code-agent** takes a different contract: it edits your repo, runs **your** verify command, and **refuses to finish until that command exits `0`**. No exit `0`, no “done.” That is fail closed — the only success that counts.

---

## What you need

| Item | Why |
|------|-----|
| `code-agent` binary | [GitHub Releases](https://github.com/kramlipi/code-agent-binaries/releases) or Docker `ghcr.io/kramlipi/code-agent:latest` |
| LLM key | `GEMINI_API_KEY`, `OPENAI_API_KEY`, or `ANTHROPIC_API_KEY` + optional `CODE_AGENT_MODEL` |
| A saved failure log | From CI or local `tee` |
| `--verify-cmd` | **Same command CI uses** — `pytest -q`, `go test ./...`, etc. |
| `-w PATH` | Root of the repo you want fixed |

See [Quick Start](../quick-start.md) for install and key setup.

---

## Step 1 — Capture the failed CI log

### From GitHub Actions

When you know the run id (from the Actions UI or `gh run list`):

```bash
gh run view 12345678901 --log-failed 2>&1 | tee /tmp/ci.log
echo "Saved log; exit code of gh: $?"
```

`--log-failed` trims to failing steps — much easier for parsers than the full multi-job dump.

### From a local repro

If you can reproduce red locally (often faster to iterate):

```bash
cd /path/to/your-repo
pytest -q 2>&1 | tee /tmp/ci.log
echo "Test exit code: $?"
```

Or for Go:

```bash
go test ./... 2>&1 | tee /tmp/ci.log
```

**Tip:** Keep the log path stable (`/tmp/ci.log`) so your bug-fix command is copy-pasteable across retries.

---

## Step 2 — Run the bug-fix expert

Point the expert at the log, the workspace, and **exactly** the gate CI uses:

```bash
export GEMINI_API_KEY=your-key
export CODE_AGENT_MODEL=gemini/gemini-2.0-flash   # optional

code-agent experts run bug-fix \
  --log /tmp/ci.log \
  --verify-cmd "pytest -q" \
  -w /path/to/your-repo
```

For Go projects:

```bash
code-agent experts run bug-fix \
  --log /tmp/ci.log \
  --verify-cmd "go test ./..." \
  -w /path/to/your-go-repo
```

### What happens inside

1. **Parse** — structured parsers read the log (not LLM guesswork).
2. **RCA** — correlate failures with recent diffs.
3. **Fix loop** — tool writes only; agent edits source/tests.
4. **Verify** — re-runs `--verify-cmd` until exit `0` or max iterations → **failed** (fail closed).

Success looks like:

```text
Status: done
signal_count: 1+
files_touched: [...]
```

If verify never goes green, status is **`failed`** — not a polite “almost.”

---

## Step 3 — Optional: open a draft PR

When the fix is green locally and you want a branch for review:

```bash
gh auth login   # once per machine

code-agent experts run bug-fix \
  --log /tmp/ci.log \
  --verify-cmd "pytest -q" \
  --publish \
  -w /path/to/your-repo
```

`--publish` commits, pushes, and opens a **draft** pull request (GitLab: draft MR via `glab`). The agent still must pass `--verify-cmd` before publish proceeds.

Use `--dry-run` first if you want to inspect the plan without git publish side effects (local file writes may still occur depending on config).

---

## Parsers: pytest, Go, generic

The bug-fix expert does **not** ask the model to “interpret” raw logs. It runs typed parsers:

| Parser | Typical signals |
|--------|-----------------|
| **pytest** | `FAILED`, file::test, assertion diffs, tracebacks |
| **Go** | `--- FAIL:`, package paths, build errors |
| **Generic** | Compiler errors, tracebacks, lint output when no specialist matches |

More specialists exist (TypeScript/tsc, ESLint, Rust, coverage gates) — see [Experts](../experts.md). If the log format is exotic, generic intake still extracts signals, but **explicit `--verify-cmd`** remains your proof.

---

## ENVIRONMENT ≠ CODE (read this before you rage-quit)

Verify failed with `ModuleNotFoundError: httpx`? Or `go: command not found`?

That is often **ENVIRONMENT**, not a logic bug in your app.

| Symptom | Likely kind | Default agent behavior |
|---------|-------------|------------------------|
| Assertion / wrong return value | **CODE** | Edit source or tests until verify green |
| Missing pip package on runner | **ENVIRONMENT** | Allowlisted installs (`pip install -r`, `go mod download`) — **not** rewriting app code to hide missing deps |
| Missing `go` / `node` on PATH | **ENVIRONMENT** | **Fail closed** in default mode — will **not** download Go for you |

**Do not** expect the default loop to `apt install golang` or patch your app to skip tests when the toolchain is absent. Install deps on the runner first, or see [Ultra intelligence mode](../features/ultra-intelligence.md) for opt-in toolchain install on a **trusted** machine.

If verify fails because CI never ran `pip install -r requirements.txt`, fix the workflow — don't ask the agent to delete the import.

---

## Common mistakes

| Mistake | Fix |
|---------|-----|
| Wrong `--verify-cmd` (`pytest` on a Go repo) | Match CI exactly — [Recipes](../recipes.md) |
| Log from job A, `-w` pointing at fork B | Same repo root as the failing code |
| Chatbot summary instead of a file | Always `--log /path/to/file` |
| Weaker verify after “success” | Re-run the **same** `--verify-cmd` yourself — exit `0` or it didn't work |
| Missing API key | `code-agent doctor --provider-test` |
| `--publish` without `gh` | `gh auth login`; see [Troubleshooting](../troubleshooting.md) |

---

## The rule, one more time

**`--verify-cmd` exit `0` is the only success.** Summaries, green emoji, and model confidence don't count. Invalid verifier JSON, ambiguous outcomes, and subprocess failures all **fail closed**.

That is why teams wire this beside GitHub Actions instead of replacing it: your pipeline keeps the score; kramlipi proposes edits that must survive the same gate.

---

## Next steps

- **Install tonight:** [Quick Start](../quick-start.md)
- **Copy-paste recipes:** [Recipe Book](../recipes.md)
- **Questions or pilot:** cluevion@gmail.com

Download the binary, save one red log, run one `--verify-cmd`. When exit code is `0`, you're done — not when the model says you are.
