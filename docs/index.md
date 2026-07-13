---
title: Kramlipi Docs — code-agent
description: >-
  Increase code coverage, fix broken CI builds, and get automated PR line-comment
  reviews with code-agent. Binary download first; verify-gated AI for GitHub CI.
keywords: >-
  increase code coverage, fix broken CI, PR code review comments, code-agent,
  failing unit tests, GEMINI_API_KEY, verify-cmd
---

# KramLipi Code agent

**Increase your code coverage and review automatically.**

Developers ship code faster — but unit tests and failed builds pile up.
This agent fixes that in the **CI pipeline**.

**`code-agent`** reads your **git repo**, edits with AI + tools, proves work with a **verify command**, and can open a **draft MR** or post **PR line comments**.

---

## Quick start

### 1. Binary first (recommended)

Download Linux / macOS / Windows:

**[Google Drive](https://drive.google.com/drive/folders/11iuNWM13SjrlKastaA_2FaMz4tGg9_QX?usp=sharing)** · **[GitHub Releases](https://github.com/kramlipi/code-agent-binaries/releases)** · **[Release notes](release-notes.md)**

```bash
chmod +x code-agent   # Linux / macOS
# Windows: code-agent.exe
```

### 2. ENV (Gemini)

Key from [Google AI Studio](https://aistudio.google.com/):

```bash
export CODE_AGENT_MODEL=gemini/gemini-2.0-flash
export GEMINI_API_KEY=YOUR_SECRET_KEY
```

### 3. What do you want to do? (commands)

#### Increase code coverage

**Pain:** Coverage gate blocks merge.  
**Fix:** Agent adds tests; your verify command must still exit `0`.

```bash
code-agent run "increase unit test coverage" \
  -w /path/to/your-repo \
  --verify-cmd "go test ./..."
```

Python: `--verify-cmd "pytest -q --cov=PACKAGE --cov-fail-under=80"` → [Coverage](coverage.md)

#### Fix a broken build / failing tests

**Pain:** CI failed; log is unreadable; you need a scoped green fix.  
**Fix:** Parse log → edit code → re-run the same CI command.

```bash
go test ./... 2>&1 | tee /tmp/ci.log
# or: pytest -q 2>&1 | tee /tmp/ci.log

code-agent experts run bug-fix \
  --log /tmp/ci.log \
  --verify-cmd "go test ./..." \
  -w /path/to/your-repo
```

Language walkthroughs: [Python](examples/python.md) · [Go](examples/go.md) · [Java](examples/java.md)

#### Review a PR (inline line comments)

**Pain:** PRs merge without a first-pass review for bugs / nits / security smells.  
**Fix:** LLM reviews the PR diff and posts **GitHub inline comments** (comment-only).

```bash
export GH_TOKEN=...   # or GITHUB_TOKEN in Actions

code-agent experts run code-review --pr 42 -w /path/to/your-repo
code-agent experts run code-review --pr 42 --dry-run -w /path/to/your-repo
```

More: [Experts](experts.md) · [Use cases](use-cases.md)

#### Other features

| I want to… | Do this | Detail |
|------------|---------|--------|
| Run fewer tests on a PR | `code-agent experts run test-intel --pr N -w .` | [Experts](experts.md) |
| Babysit PR until green | `code-agent experts watch --pr N --verify-cmd "…" -w .` | [Recipes](recipes.md) |
| Find missing metrics | `code-agent experts run monitoring-expert -w . --dry-run` | [Experts](experts.md) |
| Alert → reliability fix | `code-agent experts run sre-expert --log alert.json -w .` | [Use cases](use-cases.md) |
| Canary / deploy gate | `code-agent experts run deploy-guard --metrics-file m.json` | [Use cases](use-cases.md) |

| Flag | Meaning |
|------|---------|
| `-w` | Repo folder the agent may edit |
| `--verify-cmd` | Must exit `0` — success is not model opinion |

Full walkthrough: **[Quick Start](quick-start.md)** · 1-minute: **[Get started](get-started.md)**

### Pricing

| Free | Team $49/mo | Business $199/mo |
|------|-------------|------------------|
| Prove one green verify (capped) | Commercial CI | + PR babysit / higher volume |

→ [Get started — Pricing](get-started.md#pricing-adoption--revenue)

---

### 4. Docker (second choice)

```bash
docker pull ghcr.io/kramlipi/code-agent:latest

docker run --rm -it \
  -e CODE_AGENT_MODEL \
  -e GEMINI_API_KEY \
  -v "$PWD:/workspace" \
  ghcr.io/kramlipi/code-agent:latest \
  run "increase unit test coverage" \
  --verify-cmd "go test ./..." \
  -w /workspace
```

Image: `ghcr.io/kramlipi/code-agent:latest` · [GHCR packages](https://github.com/kramlipi?tab=packages)

---

## After the quick commands

| Next | Why |
|------|-----|
| [Get started](get-started.md) | Binary first, use cases, pricing, how to run |
| [Quick Start](quick-start.md) | Install paths, flags, container mapping |
| [Use cases](use-cases.md) | Pain → command → benefit |
| [Pains](pains.md) | Full pain catalog |
| [Commands](commands.md) | Every CLI flag |
| [Experts](experts.md) | bug-fix, code-review, test-intel, … |
| [Coverage](coverage.md) | Raise coverage with pytest-cov |
| [Security overview](https://github.com/kramlipi/ai-code-agent/blob/main/docs/SECURITY-COMPLIANCE.md) | Enterprise trust / data flow |
| [Deployment modes](https://github.com/kramlipi/ai-code-agent/blob/main/docs/DEPLOYMENT-MODES.md) | Local binary · CI · local UI |
| [config](https://github.com/kramlipi/ai-code-agent/blob/main/config.example.yaml) | All config knobs |

---

## How verify works

```bash
--verify-cmd "pytest -q"
```

| Exit | Meaning |
|------|---------|
| `0` | Success |
| `1` | Config / doctor problem |
| `2` | Agent ran but verify (or post) failed |

The agent **refuses** to edit `.github/workflows/**` to cheat CI.

---

## Site

- **Docs:** [https://kramlipi.github.io/](https://kramlipi.github.io/)
- **Product:** [github.com/kramlipi/ai-code-agent](https://github.com/kramlipi/ai-code-agent)
- **Binaries:** [Drive](https://drive.google.com/drive/folders/11iuNWM13SjrlKastaA_2FaMz4tGg9_QX?usp=sharing) · [Releases](https://github.com/kramlipi/code-agent-binaries/releases)
- **Search:** `Ctrl+K` / `Cmd+K`
