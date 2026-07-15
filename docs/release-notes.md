# Release notes

**Product:** kramlipi code-agent  
**Binaries:** [GitHub Releases](https://github.com/kramlipi/code-agent-binaries/releases) (binaries only — no product source)  
**Contact:** cluevion@gmail.com

---

## Distribution policy

- **Public downloads:** [code-agent-binaries Releases](https://github.com/kramlipi/code-agent-binaries/releases) — **binary assets only**
- **Private:** product source (`ai-code-agent`)
- GitHub always shows automatic “Source code (zip/tar.gz)” on every Release. On the binaries repo that archive is **only a README** — ignore it; download the `code-agent-*` files.

---

## What it does (exactly)

code-agent is a **verify-gated coding agent**.

1. You give a **goal** and a **`--verify-cmd`** (the check you already trust).
2. It **edits your repo** with tools (read / write / search).
3. It runs your verify command.
4. It **stops only when that command exits 0** — or it fails. It never marks success from chat alone.

**Success = your command’s exit code, not the model’s opinion.**

---

## What this release supports

| It does | It does not |
|---------|-------------|
| Fix **failing unit tests** until `pytest` / `go test` is green | Promise perfect new test suites from scratch |
| Fix **localized compile errors** until `go build` is green | Install Go / apt / downgrade toolchains |
| Repair from a **failure log** (`bug-fix`) until the same verify is green | Replace CI vendors or act as Cursor |
| Open a draft PR after green (when git/`gh` available) | Edit workflows to fake a green build |

**You must:** have the toolchain installed, and pass the real `--verify-cmd`.

---

## Commands

```bash
export CODE_AGENT_MODEL=gemini/gemini-3.1-flash-lite
export GEMINI_API_KEY=YOUR_KEY

# Failing unit tests
code-agent run \
  "Make the failing unit tests pass. Minimal edits. Do not delete tests." \
  --verify-cmd "python3 -m pytest -q" \
  -w /path/to/package

# Go compile errors
code-agent run \
  "Make go build ./... succeed. Fix compile errors only." \
  --verify-cmd "go build ./..." \
  -w /path/to/module

# From a CI / local failure log
code-agent experts run bug-fix \
  --log /tmp/fail.log \
  --verify-cmd "python3 -m pytest -q" \
  -w /path/to/repo
```

More: [Get started](get-started.md) · [Commands](commands.md)

---

## Published use cases

1. **Red unit test → green** (same pytest / go test)  
2. **Red build → green** (same go build)  
3. **Failure log → fix** (same verify until exit 0)

---

## 0.1.2

- **Economy mode off by default** — full quality; opt in with `CODE_AGENT_ECONOMY_MODE=true`
- **Code-review CI copy-paste** — GitHub Actions, GitLab CI, Azure Pipelines ([guide](code-review-ci.md))
- **`--diff-file`** for code-review on GitLab/Azure/local unified diffs
- Linux + Windows binaries on [Releases](https://github.com/kramlipi/code-agent-binaries/releases)

## 0.1.x highlights

- Verify-gated agent loop: edit → run your check → retry until green  
- `bug-fix` expert for CI / local logs  
- `code-review` expert for PR/MR first-pass findings  
- Linux + Windows binaries on [Releases](https://github.com/kramlipi/code-agent-binaries/releases)  
- Honest scope: we only claim **red check → same check green**
