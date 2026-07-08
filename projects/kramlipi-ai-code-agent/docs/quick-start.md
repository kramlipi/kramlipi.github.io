---
title: Quick Start
description: >-
  Install the code-agent binary, set GEMINI_API_KEY, run your first command,
  then fix failing unit tests in a git repo with explained flags.
keywords: install code-agent, GEMINI_API_KEY, verify-cmd, workspace, bug-fix
---

# Quick Start

Two ways to run `code-agent`:

| Path | When to use |
|------|-------------|
| **[Container image (GHCR)](#step-1--pull-the-container-image-recommended)** | You want the fastest start — pull and run |
| **[pip install from source](#step-1b--install-from-source)** | You are developing code-agent itself |

---

## Step 1 — Pull the container image (recommended)

`code-agent` is published on **GitHub Container Registry**:

```text
ghcr.io/kramlipi/code-agent:latest
```

View packages: [github.com/kramlipi → Packages](https://github.com/kramlipi?tab=packages)

### Pull the image

=== "Docker"

    ```bash
    docker pull ghcr.io/kramlipi/code-agent:latest
    ```

=== "Podman"

    ```bash
    podman pull ghcr.io/kramlipi/code-agent:latest
    ```

!!! note "Private package"
    If the package is private, login first:

    ```bash
    echo YOUR_GITHUB_PAT | docker login ghcr.io -u kramlipi --password-stdin
    ```

    Token needs at least `read:packages` (and `repo` if the package is private).

### Set provider API keys

Use **separate variables per provider**:

| Provider | Variables |
|----------|-----------|
| **Gemini** | `CODE_AGENT_MODEL=gemini/gemini-2.0-flash` + `GEMINI_API_KEY` |
| **OpenAI** | `CODE_AGENT_MODEL=openai/gpt-4o` + `OPENAI_API_KEY` |
| **Anthropic** | `CODE_AGENT_MODEL=anthropic/claude-3-5-sonnet-20241022` + `ANTHROPIC_API_KEY` |
| **DeepSeek** | `CODE_AGENT_MODEL=deepseek/deepseek-chat` + `DEEPSEEK_API_KEY` |
| **Proxy** | `CODE_AGENT_MODEL=openai/gpt-4o` + `CODE_AGENT_API_BASE` + `CODE_AGENT_API_KEY` |

=== "Gemini (Linux / macOS / WSL)"

    ```bash
    export CODE_AGENT_MODEL=gemini/gemini-2.0-flash
    export GEMINI_API_KEY="your-key"
    ```

=== "Gemini (Windows PowerShell)"

    ```powershell
    $env:CODE_AGENT_MODEL = "gemini/gemini-2.0-flash"
    $env:GEMINI_API_KEY = "your-key"
    ```

=== "OpenAI"

    ```bash
    export CODE_AGENT_MODEL=openai/gpt-4o
    export OPENAI_API_KEY="your-key"
    ```

=== "Proxy / OpenAI-compatible"

    ```bash
    export CODE_AGENT_MODEL=openai/gpt-4o
    export CODE_AGENT_API_BASE="http://127.0.0.1:8080/v1"
    export CODE_AGENT_API_KEY="your-proxy-key"
    ```

Keys can come from **host OS environment variables** or be passed with `-e` on `docker run`.

### How container arguments are passed

The image `ENTRYPOINT` is `code-agent`. **No special Docker-only flags are required** — anything after the image name is the normal CLI.

```bash
docker run ... ghcr.io/kramlipi/code-agent:latest doctor --provider-test
```

runs inside the container as:

```bash
code-agent doctor --provider-test
```

```bash
docker run ... ghcr.io/kramlipi/code-agent:latest \
  run "Fix tests" --verify-cmd "pytest -q" -w /workspace
```

runs as:

```bash
code-agent run "Fix tests" --verify-cmd "pytest -q" -w /workspace
```

| Docker / env | Meaning |
|--------------|---------|
| `-e GEMINI_API_KEY` / `-e OPENAI_API_KEY` / … | provider key for the model |
| `-e CODE_AGENT_MODEL` | LiteLLM model string |
| `-v "$PWD:/workspace"` | mount **your** git repo into the container |
| `code-agent … -w /workspace` | workspace jail — must match the mount |
| `--verify-cmd "…"` | shell command that must exit `0` |

!!! tip "Mount vs `-w`"
    `-v host:/workspace` is the Docker mount.  
    `-w /workspace` is the **code-agent** flag (same as host install).  
    Use both together.

Podman uses the same pattern (`podman run … IMAGE <subcommand> [flags]`).

### Run `doctor`

Mount **your project repo** to `/workspace`. The agent only edits files inside that mount.

=== "Docker (bash)"

    ```bash
    cd /path/to/your-repo

    docker run --rm -it \
      -e CODE_AGENT_MODEL \
      -e GEMINI_API_KEY \
      -v "$PWD:/workspace" \
      ghcr.io/kramlipi/code-agent:latest \
      doctor --provider-test
    ```

=== "Docker (PowerShell)"

    ```powershell
    cd D:\path\to\your-repo

    docker run --rm -it `
      -e CODE_AGENT_MODEL `
      -e GEMINI_API_KEY `
      -v "${PWD}:/workspace" `
      ghcr.io/kramlipi/code-agent:latest `
      doctor --provider-test
    ```

=== "Podman"

    ```bash
    podman run --rm -it \
      -e CODE_AGENT_MODEL \
      -e GEMINI_API_KEY \
      -v "$PWD:/workspace" \
      ghcr.io/kramlipi/code-agent:latest \
      doctor --provider-test
    ```

| Flag / mount | Meaning |
|--------------|---------|
| `-v "$PWD:/workspace"` | Your git repo — agent reads/writes here |
| `-w /workspace` | Workspace path **inside** the container (always `/workspace` when using this mount) |
| `-e GEMINI_API_KEY` | Provider API key (use `OPENAI_API_KEY`, etc. for other providers) |
| `doctor --provider-test` | Checks deps + sends one test request to the LLM |

**Expected:** exit code `0`, message like `Provider test ok`.

### Fix failing unit tests (container)

**Python:**

```bash
cd /path/to/your-python-repo

docker run --rm -it \
  -e CODE_AGENT_MODEL \
  -e GEMINI_API_KEY \
  -v "$PWD:/workspace" \
  ghcr.io/kramlipi/code-agent:latest \
  run "Fix all failing unit tests. Minimal changes only — no refactors." \
  --verify-cmd "pytest -q" \
  -w /workspace
```

**Go:**

```bash
cd /path/to/your-go-repo

docker run --rm -it \
  -e CODE_AGENT_MODEL \
  -e GEMINI_API_KEY \
  -v "$PWD:/workspace" \
  ghcr.io/kramlipi/code-agent:latest \
  run "Fix all failing Go tests. Minimal changes only." \
  --verify-cmd "go test -v ./..." \
  -w /workspace
```

**bug-fix expert from a saved log:**

```bash
pytest -q 2>&1 | tee /tmp/ci.log

docker run --rm -it \
  -e CODE_AGENT_MODEL \
  -e GEMINI_API_KEY \
  -v "/path/to/your-repo:/workspace" \
  -v "/tmp/ci.log:/tmp/ci.log:ro" \
  ghcr.io/kramlipi/code-agent:latest \
  experts run bug-fix \
  --log /tmp/ci.log \
  --verify-cmd "pytest -q" \
  -w /workspace
```

### Interactive chat (container)

```bash
docker run --rm -it \
  -e CODE_AGENT_MODEL \
  -e GEMINI_API_KEY \
  -v "$PWD:/workspace" \
  ghcr.io/kramlipi/code-agent:latest \
  chat -w /workspace
```

Type `exit` to quit.

### What is inside the image

- Python 3.11 + `code-agent` CLI
- `ripgrep`, `git`
- Default entrypoint: `code-agent`

**Not included:** language toolchains (`go`, `npm`, `maven`). If `--verify-cmd` needs them, run verify on the host or use a custom image that adds those tools.

### Pin a specific build

Every publish also tags the commit SHA. Prefer pin when you need a reproducible image:

| Reference | Use when |
|-----------|----------|
| `ghcr.io/kramlipi/code-agent:latest` | newest publish |
| `ghcr.io/kramlipi/code-agent:sha-<commit>` | specific workflow build |
| `ghcr.io/kramlipi/code-agent@sha256:<digest>` | immutable exact image |

```bash
docker pull ghcr.io/kramlipi/code-agent:sha-84d5ecf

# Example digests (replace with yours from the package page):
# docker pull ghcr.io/kramlipi/code-agent@sha256:438cb52b818c8af735c1ad5af4c4a8eb56a2ec9c23274a4503d112c57bf64816
```

Use `latest` for newest; use `sha-…` or `@sha256:…` to pin.

---

## Step 1b — Install from source

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
