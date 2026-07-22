---
title: Quick Start
description: >-
  Download the code-agent binary, set Gemini / Claude / OpenAI API keys, then
  increase coverage, fix broken builds, or post PR line reviews.
keywords: >-
  install code-agent, GEMINI_API_KEY, ANTHROPIC_API_KEY, OPENAI_API_KEY,
  Claude, Gemini, binary download, verify-cmd, Docker GHCR
---

!!! info "Primary start page"
    **[Get started](get-started.md)** is the canonical entry. This page keeps the full quick-start reference for deep links.

# Quick Start

Developers ship code faster — but unit tests and failed builds pile up.
This agent fixes that in the **CI pipeline** (and locally with the same commands).

Full docs: [https://kramlipi.github.io/](https://kramlipi.github.io/) · [Get started](get-started.md)

---

## These are the only steps that matter

### 1. Binary first (recommended)

**[Google Drive](https://drive.google.com/drive/folders/11iuNWM13SjrlKastaA_2FaMz4tGg9_QX?usp=sharing)** · [GitHub Releases](https://github.com/kramlipi/code-agent-binaries/releases)

```bash
chmod +x code-agent   # Linux / macOS
./code-agent doctor --provider-test
```

Windows: download `code-agent.exe` → `.\code-agent.exe doctor --provider-test`

More binary detail: [Step 1c — Download standalone binary](#step-1c--download-standalone-binary)

### 2. ENV (pick a model + API key)

Set **`CODE_AGENT_MODEL`** (LiteLLM string) and the matching provider key.

#### Gemini (default / recommended)

Key from [Google AI Studio](https://aistudio.google.com/):

```bash
export CODE_AGENT_MODEL=gemini/gemini-2.0-flash
# also fine: gemini/gemini-3.1-flash-lite
export GEMINI_API_KEY=YOUR_SECRET_KEY
# aliases: GOOGLE_API_KEY · Windows user env geminikey
```

#### Claude (Anthropic)

Key from [Anthropic Console](https://console.anthropic.com/):

```bash
export CODE_AGENT_MODEL=anthropic/claude-sonnet-4-20250514
# or: anthropic/claude-3-5-haiku-latest
export ANTHROPIC_API_KEY=YOUR_SECRET_KEY
```

#### OpenAI

Key from [OpenAI API keys](https://platform.openai.com/api-keys):

```bash
export CODE_AGENT_MODEL=openai/gpt-4o
export OPENAI_API_KEY=YOUR_SECRET_KEY
```

#### Cursor?

**Cursor does not expose a public chat API** for third-party CLIs like `code-agent`.  
Use **Gemini, Claude, or OpenAI** with kramlipi; keep Cursor as your editor.  
OpenRouter / OpenAI-compatible proxies work (see table below).

#### Env reference

| Variable | When | Get key |
|----------|------|---------|
| `CODE_AGENT_MODEL` | Always | LiteLLM model string |
| `GEMINI_API_KEY` / `GOOGLE_API_KEY` | `gemini/…` | [AI Studio](https://aistudio.google.com/) |
| `ANTHROPIC_API_KEY` | `anthropic/…` | [Anthropic](https://console.anthropic.com/) |
| `OPENAI_API_KEY` | `openai/…` | [OpenAI](https://platform.openai.com/api-keys) |
| `DEEPSEEK_API_KEY` | `deepseek/…` | DeepSeek |
| `OPENROUTER_API_KEY` | `openrouter/…` | [OpenRouter](https://openrouter.ai/) |
| `CODE_AGENT_API_BASE` | Custom / local proxy | Your `/v1` URL |
| `CODE_AGENT_API_KEY` | Custom base | Proxy key |
| `CODE_AGENT_ECONOMY_MODE` | Optional | `true` to save cost (default **off**) |

```bash
# DeepSeek
export CODE_AGENT_MODEL=deepseek/deepseek-chat
export DEEPSEEK_API_KEY=YOUR_SECRET_KEY

# OpenRouter
export CODE_AGENT_MODEL=openrouter/anthropic/claude-3.5-sonnet
export OPENROUTER_API_KEY=YOUR_SECRET_KEY

# OpenAI-compatible proxy
export CODE_AGENT_MODEL=openai/my-model
export CODE_AGENT_API_BASE=https://your-proxy.example/v1
export CODE_AGENT_API_KEY=YOUR_PROXY_KEY
```

!!! tip "Model string"
    Always use the LiteLLM form: `gemini/…`, `anthropic/…`, `openai/…`.

### 3. By use case — what do you want to do?

#### Increase code coverage

**Pain:** Coverage gate / missing tests.  
**Do this:**

```bash
code-agent run "increase unit test coverage" \
  -w /path/to/your-repo \
  --verify-cmd "go test ./..."
```

| Language | Example `--verify-cmd` |
|----------|------------------------|
| Go | `go test ./...` |
| Python | `pytest -q --cov=PACKAGE --cov-fail-under=80` |
| Java | `mvn test` |

→ [Coverage](coverage.md) · [Use cases](use-cases.md#4-coverage-gate-blocking-merge)

#### Fix a broken build / failing tests

**Pain:** CI red; huge log.  
**Do this:**

```bash
go test ./... 2>&1 | tee /tmp/ci.log

code-agent experts run bug-fix \
  --log /tmp/ci.log \
  --verify-cmd "go test ./..." \
  -w /path/to/your-repo
```

→ [Python](examples/python.md) · [Go](examples/go.md) · [Java](examples/java.md)

#### Review a PR (inline comments)

**Pain:** No automated first-pass line review.  
**Do this:**

```bash
export GH_TOKEN=...   # or gh auth / GITHUB_TOKEN in CI

code-agent experts run code-review --pr 42 -w /path/to/your-repo
code-agent experts run code-review --pr 42 --dry-run -w /path/to/your-repo
```

#### Add code-review to CI (copy-paste)

| Platform | What you get |
|----------|----------------|
| **GitHub Actions** | Inline PR review comments |
| **GitLab CI** | Findings artifact + optional MR note |
| **Azure DevOps** | Findings pipeline artifact |

→ Full YAML: **[Code review CI](code-review-ci.md)**

```bash
# GitLab / Azure / local — unified diff
git diff main...HEAD > /tmp/mr.diff
code-agent experts run code-review --diff-file /tmp/mr.diff -w .
```

Economy mode is **off by default**. Opt in: `CODE_AGENT_ECONOMY_MODE=true`.

→ [Use cases](use-cases.md) · [Experts](experts.md)

#### Other features

| I want to… | Command | Detail |
|------------|---------|--------|
| Impacted tests only | `experts run test-intel --pr N` | [Experts](experts.md) |
| Babysit PR | `experts watch --pr N --verify-cmd "…"` | [Recipes](recipes.md) |
| Missing metrics | `experts run monitoring-expert --dry-run` | [Use cases](use-cases.md) |
| Alert → fix | `experts run sre-expert --log alert.json` | [Pains](pains.md) |
| Deploy gate | `experts run deploy-guard --metrics-file m.json` | [Use cases](use-cases.md) |

| Flag | Meaning |
|------|---------|
| `-w` / `--workspace` | Folder path of the git repo to edit |
| `--verify-cmd` | Shell command that must exit `0` |

#### Ultra intelligence (missing Go / toolchain)

Default mode does **not** install Go. On a **trusted** host, opt in:

```bash
code-agent run "Make Go unit tests pass. Minimal changes." \
  --verify-cmd "go test ./..." \
  --autonomy cascade \
  --approve-privileged \
  -w /path/to/go-project
```

Full demo + why this is opt-in: **[Ultra intelligence mode](ultra-intelligence.md)**

### 4. Docker (optional — second choice)

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

Inside Docker, mount the repo to `/workspace` and pass `-w /workspace`.

---

## More install paths

| Path | When to use |
|------|-------------|
| **[Standalone binary](#step-1c--download-standalone-binary)** | Native download — preferred |
| **[Container image (GHCR)](#step-1--pull-the-container-image)** | No local binary — pull and run |
| **[pip install from source](#step-1b--install-from-source)** | Developing code-agent itself |

---

## Step 1 — Pull the container image

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

Use **separate variables per provider** (same as [§2 ENV](#2-env-pick-a-model-api-key) above):

| Provider | Variables |
|----------|-----------|
| **Gemini** | `CODE_AGENT_MODEL=gemini/gemini-2.0-flash` + `GEMINI_API_KEY` |
| **Claude** | `CODE_AGENT_MODEL=anthropic/claude-sonnet-4-20250514` + `ANTHROPIC_API_KEY` |
| **OpenAI** | `CODE_AGENT_MODEL=openai/gpt-4o` + `OPENAI_API_KEY` |
| **DeepSeek** | `CODE_AGENT_MODEL=deepseek/deepseek-chat` + `DEEPSEEK_API_KEY` |
| **OpenRouter** | `CODE_AGENT_MODEL=openrouter/…` + `OPENROUTER_API_KEY` |
| **Proxy** | `CODE_AGENT_MODEL=openai/…` + `CODE_AGENT_API_BASE` + `CODE_AGENT_API_KEY` |

!!! note "Cursor"
    Cursor has **no public chat API** for `code-agent`. Use Gemini, Claude, or OpenAI keys.

=== "Gemini (Linux / macOS / WSL)"

    ```bash
    export CODE_AGENT_MODEL=gemini/gemini-2.0-flash
    export GEMINI_API_KEY="your-key"
    ```

=== "Claude"

    ```bash
    export CODE_AGENT_MODEL=anthropic/claude-sonnet-4-20250514
    export ANTHROPIC_API_KEY="your-key"
    ```

=== "OpenAI"

    ```bash
    export CODE_AGENT_MODEL=openai/gpt-4o
    export OPENAI_API_KEY="your-key"
    ```

=== "Gemini (Windows PowerShell)"

    ```powershell
    $env:CODE_AGENT_MODEL = "gemini/gemini-2.0-flash"
    $env:GEMINI_API_KEY = "your-key"
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

## Step 1c — Download standalone binary

**Easiest download (Google Drive):**  
[Kramlipi-code-agent binaries](https://drive.google.com/drive/folders/11iuNWM13SjrlKastaA_2FaMz4tGg9_QX?usp=sharing)

Folders: `linux/` · `macos/` · `windows/`

Also published as **GitHub Release** assets on this docs repo:

**[github.com/kramlipi/code-agent-binaries/releases](https://github.com/kramlipi/code-agent-binaries/releases)**

Release tags look like `code-agent-v0.1.0`. Assets:

| Platform | File |
|----------|------|
| Linux | `code-agent-v0.1.0-linux` |
| macOS | `code-agent-v0.1.0-macos` |
| Windows | `code-agent-v0.1.0-windows.exe` |

=== "Linux"

    ```bash
    # From Google Drive: download linux/code-agent, then:
    chmod +x code-agent
    ./code-agent doctor --provider-test
    ```

    Or from GitHub Releases:

    ```bash
    curl -fsSL -o code-agent \
      https://github.com/kramlipi/code-agent-binaries/releases/download/code-agent-v0.1.0/code-agent-v0.1.0-linux
    chmod +x code-agent
    ./code-agent doctor --provider-test
    ```

=== "macOS"

    ```bash
    # From Google Drive: download macos/code-agent, then:
    chmod +x code-agent
    ./code-agent doctor --provider-test
    ```

    Or from GitHub Releases:

    ```bash
    curl -fsSL -o code-agent \
      https://github.com/kramlipi/code-agent-binaries/releases/download/code-agent-v0.1.0/code-agent-v0.1.0-macos
    chmod +x code-agent
    ./code-agent doctor --provider-test
    ```

=== "Windows (PowerShell)"

    ```powershell
    # From Google Drive: download windows/code-agent.exe, then:
    .\code-agent.exe doctor --provider-test
    ```

    Or from GitHub Releases:

    ```powershell
    Invoke-WebRequest -Uri "https://github.com/kramlipi/code-agent-binaries/releases/download/code-agent-v0.1.0/code-agent-v0.1.0-windows.exe" `
      -OutFile "code-agent.exe"
    .\code-agent.exe doctor --provider-test
    ```

!!! note "ripgrep"
    Standalone binaries still need [`rg`](https://github.com/BurntSushi/ripgrep) on your PATH for code search.

Set `GEMINI_API_KEY` / `CODE_AGENT_MODEL` the same way as in [Set provider API keys](#set-provider-api-keys) above, then continue with [Step 2](#step-2--first-command).

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
- [All CLI flags](features.md#commands)
- [Experts reference](features.md#experts)
- [Get started](get-started.md) (canonical entry)
