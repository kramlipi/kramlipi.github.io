---
title: Kramlipi Docs — code-agent
description: >-
  Symptom: red CI, buried logs, stalled coverage, review that does not scale.
  Solution: Kramlipi AI Code Agent — verify-gated coverage, bug-fix, and PR review.
keywords: >-
  increase code coverage, fix broken CI, PR code review comments, code-agent,
  failing unit tests, GEMINI_API_KEY, verify-cmd
---

# KramLipi Code agent

**Symptom → solution.**

Symptom: your PR is red, the CI log is thousands of lines, coverage gates stall merges, and review still sits on humans—while chat AI claims “fixed” with no proof. You lose nights to archaeology instead of shipping. Solution: **Kramlipi AI Code Agent**. It reads your git repo and the failure signal, edits with real tools, and only stops when **your** verify command exits `0`. Coverage, bug-fix, and PR line review become measured outcomes—not guesses.

[How kramlipi helps — visual collage →](get-started.md#how-kramlipi-helps-collage)

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

Python: `--verify-cmd "pytest -q --cov=PACKAGE --cov-fail-under=80"` → [Use cases → Coverage](use-cases.md#4-coverage-gate-blocking-merge) · [Features → Coverage](features.md#coverage)

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

Language walkthroughs: [Python](use-cases.md#python-example) · [Go](use-cases.md#go-example) · [Java](use-cases.md#java-example)

#### Review a PR (inline line comments)

**Pain:** PRs merge without a first-pass review for bugs / nits / security smells.  
**Fix:** LLM reviews the PR diff and posts **GitHub inline comments** (comment-only).

```bash
export GH_TOKEN=...   # or GITHUB_TOKEN in Actions

code-agent experts run code-review --pr 42 -w /path/to/your-repo
code-agent experts run code-review --pr 42 --dry-run -w /path/to/your-repo
```

More: [Use cases](use-cases.md) · [Features](features.md)

#### Other features

| I want to… | Do this | Detail |
|------------|---------|--------|
| Run fewer tests on a PR | `code-agent experts run test-intel --pr N -w .` | [Use cases](use-cases.md#2-slow-ci--stop-running-the-full-suite) |
| Babysit PR until green | `code-agent experts watch --pr N --verify-cmd "…" -w .` | [Use cases](use-cases.md#51-same-pr-keeps-failing--babysit-until-green) |
| Find missing metrics | `code-agent experts run monitoring-expert -w . --dry-run` | [Features](features.md#experts) |
| Alert → reliability fix | `code-agent experts run sre-expert --log alert.json -w .` | [Use cases](use-cases.md#7-sre-and-incidents) |
| Canary / deploy gate | `code-agent experts run deploy-guard --metrics-file m.json` | [Features](features.md#experts) |

| Flag | Meaning |
|------|---------|
| `-w` | Repo folder the agent may edit |
| `--verify-cmd` | Must exit `0` — success is not model opinion |

Full walkthrough: **[Get started](get-started.md)** (only start page)

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
| [Get started](get-started.md) | Binary, ENV, use cases, Docker UI, pricing (only start page) |
| [Use cases](use-cases.md) | Playbooks + pains + Python/Go/Java examples |
| [Features](features.md) | Experts, CLI, recipes, coverage (full reference) |
| [Tutorials](articles/index.md) | Walkthroughs (Python / Go / Java / coverage / review) |
| [Help](troubleshooting.md) | Exit codes and failures |
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
