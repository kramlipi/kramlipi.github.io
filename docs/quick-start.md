---
title: Quick Start
description: >-
  Install the code-agent binary, set GEMINI_API_KEY, run your first command,
  then fix failing unit tests in a git repo with explained flags.
keywords: install code-agent, GEMINI_API_KEY, verify-cmd, workspace, bug-fix
---

# Quick Start

Follow these steps in order. No shortcuts.

---

## Step 1 — Get the `code-agent` binary

`code-agent` is installed as a **CLI command** when you `pip install` the project (it is not a separate download).

```bash
# Clone the product repo
git clone https://github.com/kramlipi/ai-code-agent.git
cd ai-code-agent

# Create virtualenv (required on Ubuntu/Debian)
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\Activate.ps1

# Install — this creates the binary
pip install -e ".[dev]"

# Copy config template
cp config.example.yaml config.yaml
```

**Check the binary exists:**

```bash
which code-agent
code-agent --version
```

**Expected:**

```text
/path/to/ai-code-agent/.venv/bin/code-agent
```

If `which code-agent` prints nothing → run `source .venv/bin/activate` again.

**Also install ripgrep** (required for code search):

```bash
# Ubuntu/Debian
sudo apt install ripgrep

# macOS
brew install ripgrep
```

---

## Step 2 — Set `GEMINI_API_KEY`

Get a key from [Google AI Studio](https://aistudio.google.com/apikey).

=== "Linux / macOS / WSL"

    ```bash
    export GEMINI_API_KEY="AIza..."
    ```

    Add to `~/.bashrc` or `~/.zshrc` to persist:

    ```bash
    echo 'export GEMINI_API_KEY="AIza..."' >> ~/.bashrc
    source ~/.bashrc
    ```

=== "Windows PowerShell"

    ```powershell
    $env:GEMINI_API_KEY = "AIza..."
    ```

=== "WSL + key stored in Windows"

    1. Windows → Settings → Environment variables → User → New → name `geminikey`, paste key  
    2. In WSL:

    ```bash
    code-agent env sync
    code-agent env show
    ```

**Verify key is visible (value hidden):**

```bash
code-agent env show
code-agent doctor
code-agent doctor --provider-test    # pings Gemini — optional but recommended
```

**Expected:** exit code `0`, no errors about missing API key.

---

## Step 3 — Smallest possible example

This proves install + API key + agent loop work.

```bash
cd ai-code-agent
source .venv/bin/activate

code-agent run "Add one line to README.md explaining this project is a coding agent CLI" -w .
```

### Flags used

| Flag | Long form | What it means | Why you need it |
|------|-----------|---------------|-----------------|
| `-w` | `--workspace` | **Which git repo** the agent may read/edit | Tells agent where your code lives. `.` = current folder |

**Expected on success:**

```text
Status: done
Files: README.md
```

**Exit code:** `0`

!!! note "Dry run (no file changes)"
    Add `--dry-run` to test without writing files. Agent plans only; writes are blocked.

---

## Step 4 — Fix failing unit tests in **your** git repo

The agent can work on **any** repository — not only `ai-code-agent`.

**Important flags (used in every real fix):**

| Flag | What it means | Why |
|------|---------------|-----|
| `-w PATH` | Target repo root | Agent edits *that* repo's files |
| `--verify-cmd "CMD"` | Shell command that **must exit 0** | Proof the fix works — same as CI |
| `--log FILE` | Saved test/CI output | `bug-fix` expert parses errors from this file |
| `--dry-run` | No publish; may still write locally | Safe first try |
| `--publish` | Commit + push + **draft MR/PR** | Needs `gh` or `glab` logged in |
| `-c` / `--config` | Path to `config.yaml` | Override model/settings |
| `--base-branch` | MR targets this branch | Default `main` |

### Generic workflow (any language)

```bash
# 1) Go to YOUR project (example)
cd /path/to/your-git-repo

# 2) Run tests — see them fail — save log
<your-test-command> 2>&1 | tee /tmp/ci.log
echo "Exit code: $?"

# 3) Run bug-fix expert (from any terminal with code-agent in PATH)
source ~/karm/ai-code-agent/.venv/bin/activate   # or your venv

code-agent experts run bug-fix \
  --log /tmp/ci.log \
  --verify-cmd "<same-test-command-as-CI>" \
  -w /path/to/your-git-repo
```

**What happens inside:**

1. **Parse** `/tmp/ci.log` → find test failures, line numbers, files  
2. **RCA** → match errors with recent `git diff`  
3. **Fix** → edit source/tests with tools (not chat-only)  
4. **Verify** → run `--verify-cmd` until exit `0` or max iterations  

**Expected success:**

```text
Status: done
signal_count: 1+
files_touched: [...]
```

---

## Step 5 — Language-specific examples

Pick your language:

| Language | Test command | Guide |
|----------|--------------|-------|
| **Python** | `pytest -q` | [Python example →](examples/python.md) |
| **Go** | `go test -v ./...` | [Go example →](examples/go.md) |
| **Java** | `mvn test` or `./gradlew test` | [Java example →](examples/java.md) |

---

## Step 6 — Increase unit test coverage

When CI fails because coverage is too low:

```bash
cd /path/to/your-python-repo
source /path/to/ai-code-agent/.venv/bin/activate

pytest -q --cov=your_package --cov-report=term-missing --cov-fail-under=80 \
  2>&1 | tee /tmp/coverage.log

code-agent experts run bug-fix \
  --log /tmp/coverage.log \
  --verify-cmd "pytest -q --cov=your_package --cov-report=term-missing --cov-fail-under=80" \
  -w /path/to/your-python-repo
```

The agent is told to **add tests**, not delete production code.

Full runbook: [Coverage](coverage.md)

---

## Step 7 — Missing telemetry + merge request

Find HTTP handlers without metrics and open a draft PR:

```bash
code-agent experts run monitoring-expert \
  -w /path/to/your-repo \
  --dry-run

# When happy with dry-run output, publish MR:
code-agent experts run monitoring-expert \
  -w /path/to/your-repo \
  --publish
```

| Flag | Why |
|------|-----|
| `--dry-run` | See findings first, no git publish |
| `--publish` | Creates branch + draft MR with instrumentation changes |
| `-w` | Repo to scan |

Requires `gh auth login` (GitHub) or `glab auth login` (GitLab).

---

## Step 8 — Flaky CI failures

**What code-agent does today:**

- Parses the **current** failure log and fixes real bugs  
- **RCA** correlates failure with git diff + prior runs  
- **Dedup:** same failure fingerprint within 24h → `skipped` (avoids duplicate MRs)

**What it does not do yet:** automatic “this test is flaky” scoring from history.

**Practical workflow:**

```bash
# Save the failing CI log
code-agent experts run bug-fix \
  --log /tmp/ci.log \
  --verify-cmd "pytest -q" \
  -w /path/to/repo

# Babysit an open PR until CI stays green
code-agent experts watch --pr 42 --verify-cmd "pytest -q" -w /path/to/repo
```

---

## Exit codes

| Code | Meaning |
|------|---------|
| `0` | Success |
| `1` | Install/config/doctor problem |
| `2` | Agent ran but verify failed |

---

## Next

- [Python failing tests](examples/python.md)
- [Go failing tests](examples/go.md)
- [Java failing tests](examples/java.md)
- [All CLI flags](commands.md)
- [Experts reference](experts.md)
