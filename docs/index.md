---
title: Kramlipi Docs — code-agent
description: >-
  code-agent — AI CLI for CI failures, failing unit tests, code coverage,
  missing tests, flaky CI triage, and missing telemetry with merge requests.
keywords: code-agent, ci automation, unit tests, coverage, telemetry, merge request
---

# code-agent

**`code-agent`** is a terminal CLI that reads your **git repo**, uses AI + real tools to edit code, runs a **verify command** to prove the fix works, and optionally opens a **draft merge request**.

Use it in **CI and local development** when you need to:

| Problem | What code-agent does |
|---------|----------------------|
| **CI pipeline failed** | Reads the build log → finds root cause → fixes code → re-runs your verify command |
| **Failing unit tests** | Fixes Python (`pytest`), Go (`go test`), Java (`mvn test`), and more |
| **Low code coverage** | Adds missing unit tests (does **not** delete code to cheat coverage) |
| **Missing unit tests** | Writes new tests under `tests/` or `src/test/` |
| **Flaky / repeated CI failures** | Parses logs + git diff + run history (RCA); deduplicates same failure within 24h |
| **Slow CI** | `test-intel`: git diff → run only impacted tests |
| **Missing telemetry** | `monitoring-expert` finds handlers without Prometheus/OpenTelemetry metrics |
| **MR for telemetry gaps** | `monitoring-expert --publish` → draft PR with instrumentation fixes |

---

## Quick start (5 steps)

### Step 1 — Install the binary

```bash
git clone https://github.com/kramlipi/ai-code-agent.git
cd ai-code-agent
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\Activate.ps1
pip install -e ".[dev]"
cp config.example.yaml config.yaml

which code-agent    # must print a path
```

Also install **ripgrep**: `sudo apt install ripgrep` (Ubuntu) or `brew install ripgrep` (macOS).

### Step 2 — Set `GEMINI_API_KEY`

Get a key from [Google AI Studio](https://aistudio.google.com/apikey).

```bash
export GEMINI_API_KEY="your-key-here"
code-agent doctor
code-agent doctor --provider-test
```

### Step 3 — Smallest example

```bash
code-agent run "Add one line to README explaining this is a coding agent CLI" -w .
```

| Flag | Meaning |
|------|---------|
| `-w` / `--workspace` | Which git repo the agent may edit (`.` = current folder) |

### Step 4 — Fix failing unit tests

```bash
cd /path/to/your-repo
pytest -q 2>&1 | tee /tmp/ci.log

code-agent experts run bug-fix \
  --log /tmp/ci.log \
  --verify-cmd "pytest -q" \
  -w /path/to/your-repo
```

| Flag | Meaning |
|------|---------|
| `--log` | Saved test/CI output — expert parses errors from this file |
| `--verify-cmd` | Command that **must exit 0** — same as your CI gate |
| `-w` | Your project repo (not the code-agent install folder) |

### Step 5 — Open a draft merge request (optional)

```bash
code-agent experts run bug-fix \
  --log /tmp/ci.log \
  --verify-cmd "pytest -q" \
  -w /path/to/your-repo \
  --publish
```

Requires `gh auth login` (GitHub) or `glab auth login` (GitLab).

👉 **Full walkthrough:** [Quick Start](quick-start.md)

---

## Language examples

| Language | Guide |
|----------|--------|
| Python | [Failing pytest →](examples/python.md) |
| Go | [Failing go test →](examples/go.md) |
| Java | [Failing JUnit →](examples/java.md) |

---

## Documentation

| Page | Contents |
|------|----------|
| [Quick Start](quick-start.md) | Install, API key, flags, coverage, telemetry MR |
| [Commands](commands.md) | Full CLI reference |
| [Experts](experts.md) | bug-fix, test-intel, monitoring-expert, … |
| [Recipes](recipes.md) | Copy-paste workflows |
| [Coverage](coverage.md) | Raise unit test coverage with pytest-cov |
| [Troubleshooting](troubleshooting.md) | Exit codes, common failures |

---

## How verify works

The agent **cannot claim success** unless your command passes:

```bash
--verify-cmd "pytest -q"
```

| Exit code | Meaning |
|-----------|---------|
| `0` | Success — fix accepted |
| `1` | Config / doctor problem |
| `2` | Agent ran but verify failed |

The agent **refuses** to edit `.github/workflows/**` to cheat CI.

---

## Experts at a glance

| Expert | Use when |
|--------|----------|
| `bug-fix` | CI log has test/compiler/coverage errors |
| `test-intel` | PR CI slow — run only impacted tests |
| `monitoring-expert` | Missing metrics → optional MR |
| `deploy-guard` | Post-deploy metrics check |
| `sre-expert` | Alert JSON from Alertmanager |

[Full experts reference →](experts.md)

---

## Site

- **Docs:** [https://kramlipi.github.io/](https://kramlipi.github.io/)
- **Source:** [github.com/kramlipi/kramlipi.github.io](https://github.com/kramlipi/kramlipi.github.io)
- **Product repo:** [github.com/kramlipi/ai-code-agent](https://github.com/kramlipi/ai-code-agent)
- **Search:** `Ctrl+K` / `Cmd+K`
