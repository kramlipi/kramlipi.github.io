---
title: Linter bridge and sandbox — real static analysis on every review
description: >-
  kramlipi code-review runs allowlisted linters on changed lines before the LLM —
  ruff, eslint, golangci-lint, semgrep, and more. Optional Docker sandbox with
  preinstalled tools. Customer-hosted, no arbitrary shell.
---

# Linters on changed lines (and optional Docker sandbox)

**Public URL:** https://kramlipi.github.io/linter-sandbox/

Every PR review starts with more than a truncated diff. **kramlipi code-review** runs real linters on the lines you actually changed, turns their output into review findings, and only then asks the LLM for semantic issues. That means fewer “the linter already caught this” comments and more time on logic, security, and API breaks.

Your code stays on **your** machine or **your** CI runner. We do not run a CodeRabbit-style cloud mashup of forty tools — we run a **fixed allowlist** you can extend, with an optional **Docker sandbox** when you want the same tools everywhere without installing them on every laptop.

---

## What runs today

| Language / stack | Tool | How |
|------------------|------|-----|
| Python | **ruff** | Changed `.py` lines |
| Node, React, Vue, TypeScript | **eslint** | `.js` `.jsx` `.ts` `.tsx` `.vue` … |
| Go | **golangci-lint** | Package paths from changed `.go` files |
| Many languages (SAST) | **semgrep** | `--config auto` on changed files |
| Ruby | **rubocop** | When `rubocop` is on PATH |
| Rust | **cargo clippy** | Nearest `Cargo.toml` workspace |
| Java | **checkstyle** | When repo has `checkstyle.xml` (or known paths) |
| C / C++ | **cppcheck** | Changed source/header lines |

If a tool is missing, review **continues** — that linter is skipped, not a hard failure.

Findings are merged **before** the LLM pass and saved in `.code-agent/runs/*/review_linter.json`.

---

## Local review (host linters)

**1.** Install the tools you care about (example on Linux):

```bash
pip install ruff semgrep
npm install -g eslint
# optional: golangci-lint, rubocop, cppcheck, checkstyle, Rust toolchain for clippy
```

**2.** Review a branch diff:

```bash
export GEMINI_API_KEY=...
git diff main...HEAD > /tmp/mr.diff
code-agent experts run code-review --diff-file /tmp/mr.diff -w .
```

**3.** See what ran:

```bash
ls .code-agent/runs/*/review_linter.json
```

Linters are **on by default** (`linter_bridge: true`). To pick tools explicitly, add to `config.yaml`:

```yaml
experts:
  code_review:
    linter_tools:
      - ruff
      - eslint
      - golangci-lint
      - semgrep
```

---

## Docker sandbox (same tools on every machine)

Use this when developers do not have ruff/eslint/golangci installed locally, or when you want **network-isolated** linter runs (`--network=none` inside the container).

### Step 1 — Build the image (once per machine or publish to your registry)

From the [product repo](https://github.com/runningcodeio/ai-code-agent):

```bash
./scripts/docker/build_linter_sandbox.sh
# → tags kramlipi/linter-sandbox:0.1
```

**Image v0.1 includes:** ruff, semgrep, cppcheck, eslint, golangci-lint.  
**Host fallback:** rubocop, clippy, checkstyle if not in the image.

### Step 2 — Enable sandbox

**Environment (quick try):**

```bash
export CODE_AGENT_LINTER_SANDBOX=1
export CODE_AGENT_LINTER_SANDBOX_IMAGE=kramlipi/linter-sandbox:0.1
code-agent experts run code-review --diff-file /tmp/mr.diff -w .
```

**Config file:**

```yaml
experts:
  code_review:
    linter_sandbox: true
    linter_sandbox_image: kramlipi/linter-sandbox:0.1
```

Requires **Docker on PATH**. If Docker is missing, review falls back to host linters automatically.

### Step 3 — CI (GitHub Actions example)

Build or pull the image in your workflow, then:

```yaml
- name: PR review with linter sandbox
  env:
    GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
    CODE_AGENT_LINTER_SANDBOX: "1"
    CODE_AGENT_LINTER_SANDBOX_IMAGE: kramlipi/linter-sandbox:0.1
  run: |
    code-agent experts run code-review \
      --pr ${{ github.event.pull_request.number }} \
      -w .
```

Or pre-build in a job and push to GHCR; set `CODE_AGENT_LINTER_SANDBOX_IMAGE=ghcr.io/your-org/linter-sandbox:0.1`.

---

## How it fits with AI review

```text
PR diff
  → allowlisted linters on changed lines (host or Docker sandbox)
  → deterministic scanners (secrets, eval, …)
  → LLM review with linter + scanner context
  → inline comments / findings JSON
```

We are **not** claiming forty-linter parity with cloud review SaaS. We **are** giving you deterministic anchors on the diff, customer-hosted, with a path to add more tools via the same registry — and optional sandbox — without arbitrary shell.

---

## Safety

- Only fixed binaries may run (`ruff`, `eslint`, `golangci-lint`, `semgrep`, `rubocop`, `cargo`, `checkstyle`, `cppcheck`).
- No user-supplied shell strings.
- Sandbox containers run with **`--network=none`** and a read-write bind mount of your workspace only.

---

## Related

- [Code review in CI](code-review-ci.md) — GitHub, GitLab, Azure copy-paste  
- [Get started](get-started.md) — binary, API key, first run  
- [Experts](experts.md) — `code-review` flags  
- Product source: `docker/linter-sandbox/Dockerfile`, `linter_bridge.py`, `linter_sandbox.py`

**Try free:** https://kramlipi.github.io/get-started/ · **Contact:** cluevion@gmail.com
