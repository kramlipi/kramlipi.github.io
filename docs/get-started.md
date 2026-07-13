---
title: Get started
description: >-
  Download the code-agent binary, set GEMINI_API_KEY, then increase coverage,
  fix a broken build, or post PR line-comment reviews — one command each.
keywords: >-
  get started code-agent, binary download, increase coverage, fix broken CI,
  PR code review, GEMINI_API_KEY, verify-cmd
---

# Get started

# KramLipi Code agent

**Increase your code coverage and review automatically.**

Developers ship code faster — but unit tests and failed builds pile up.
This agent fixes that in the **CI pipeline**.

---

## 1. Binary first

**[Google Drive](https://drive.google.com/drive/folders/11iuNWM13SjrlKastaA_2FaMz4tGg9_QX?usp=sharing)** — `linux/` · `macos/` · `windows/`

Also: [GitHub Releases](https://github.com/kramlipi/code-agent-binaries/releases)

```bash
chmod +x code-agent   # Linux / macOS
```

## 2. ENV (Gemini)

Key from [Google AI Studio](https://aistudio.google.com/):

```bash
export CODE_AGENT_MODEL=gemini/gemini-2.0-flash
export GEMINI_API_KEY=YOUR_SECRET_KEY
```

## 3. What do you want to do?

### Increase code coverage

**Pain:** Coverage / missing tests block merge.  
**Do this:**

```bash
code-agent run "increase unit test coverage" \
  -w /path/to/your-repo \
  --verify-cmd "go test ./..."
```

→ [Coverage](coverage.md) · [Use cases](use-cases.md#4-coverage-gate-blocking-merge)

### Fix a broken build

**Pain:** CI red; log archaeology at midnight.  
**Do this:**

```bash
go test ./... 2>&1 | tee /tmp/ci.log

code-agent experts run bug-fix \
  --log /tmp/ci.log \
  --verify-cmd "go test ./..." \
  -w /path/to/your-repo
```

→ [Python](examples/python.md) · [Go](examples/go.md) · [Java](examples/java.md) · [Use cases](use-cases.md#1-ci-failed--you-need-a-fix-tonight)

### Review a PR (inline comments)

**Pain:** No first-pass review on every PR.  
**Do this:**

```bash
code-agent experts run code-review --pr 42 -w /path/to/your-repo
code-agent experts run code-review --pr 42 --dry-run -w /path/to/your-repo
```

→ [Use cases](use-cases.md) · [Experts](experts.md)

### Other features

| I want to… | Command | Detail |
|------------|---------|--------|
| Impacted tests only | `experts run test-intel --pr N` | [Experts](experts.md) |
| Babysit PR | `experts watch --pr N --verify-cmd "…"` | [Recipes](recipes.md) |
| Missing metrics | `experts run monitoring-expert --dry-run` | [Use cases](use-cases.md) |
| Alert → fix | `experts run sre-expert --log alert.json` | [Pains](pains.md) |

| Flag | Meaning |
|------|---------|
| `-w` | Repo path |
| `--verify-cmd` | Must exit `0` |

**Rule:** success = verify exits `0`, not model opinion.

---

## Pricing (adoption + revenue)

| Plan | Price | You get |
|------|-------|---------|
| **Community (Free)** | $0 | Prove green verify locally; capped runs; 14-day commercial eval |
| **Team — CI Repair** | **$49/mo** | Commercial CI rights, higher caps, ~5 seats |
| **Business — PR Babysit** | **$199/mo** | + `experts watch`, more seats/volume |

We do **not** give unlimited production CI away free. Details: product repo [`docs/COMMERCIAL.md`](https://github.com/kramlipi/ai-code-agent/blob/main/docs/COMMERCIAL.md) · [`docs/MONETIZATION-LICENSE.md`](https://github.com/kramlipi/ai-code-agent/blob/main/docs/MONETIZATION-LICENSE.md)

Contact / keys: **cluevion@gmail.com**

### How to run (three modes)

| Mode | When | Doc |
|------|------|-----|
| **Local binary** | Laptop fix / coverage / dry-run review | Download Drive/Releases → same CLI |
| **CI (Actions / GHCR)** | Every PR or failed workflow | Image `ghcr.io/kramlipi/code-agent` or binary on runner |
| **Local UI** | Browser demo | Docker UI gist → http://127.0.0.1:8080 |

Full steps: product [`DEPLOYMENT-MODES.md`](https://github.com/kramlipi/ai-code-agent/blob/main/docs/DEPLOYMENT-MODES.md)

### Enterprise trust (short)

Runs on **your** machine or **your** CI with **your** LLM key. We don’t host your monorepo.  
Security overview: [`SECURITY-COMPLIANCE.md`](https://github.com/kramlipi/ai-code-agent/blob/main/docs/SECURITY-COMPLIANCE.md)

---

## 4. Docker (second choice)

```bash
docker pull ghcr.io/kramlipi/code-agent:latest

docker run --rm -it \
  -e CODE_AGENT_MODEL \
  -e GEMINI_API_KEY \
  -v "/path/to/your-repo:/workspace" \
  ghcr.io/kramlipi/code-agent:latest \
  run "increase unit test coverage" \
  --verify-cmd "go test ./..." \
  -w /workspace
```

Browser UI (~60s) gists: [Linux](https://gist.github.com/kramlipi/d31f4f454cd127cfb552e5ed5e854af3) · [Windows](https://gist.github.com/kramlipi/387228f78eb47e437f578f625a101707)

---

## Next

| | |
|-|-|
| Full install | [Quick Start](quick-start.md) |
| Pain → command | [Use cases](use-cases.md) · [Pains](pains.md) |
| All flags | [Commands](commands.md) |
| Home | [index](index.md) |
