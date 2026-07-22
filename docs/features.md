---
title: Features
description: >-
  code-agent experts, CLI commands, copy-paste recipes, and coverage runbook —
  full reference merged on one page.
keywords: code-agent features, experts, cli, recipes, coverage, verify-cmd
---

# Features

Everything **code-agent** can do — experts, CLI, recipes, and coverage.  
Pain-first walkthroughs live on **[Use cases](use-cases.md)**.

---

## Experts {#experts}

!!! info "Also on merged page"
    Full content below is preserved. Same section: [features.md#experts](features.md#experts).


Experts wrap the agent loop with **intake → triage → fix → verify → publish**.

!!! info "When should I use which expert?"
    See the **[Early Adopter Use Cases](use-cases.md)** guide — each scenario explains **why**, the **command**, and the **benefit**.

```bash
code-agent experts list
```

---

## `bug-fix` — CI failure auto-remediation

| | |
|---|---|
| **When** | CI failed (compiler, tests, coverage, lint) |
| **Input** | `--log FILE` or `--run-id GITHUB_RUN_ID` |
| **Verify** | `--verify-cmd` (should match CI) |

```bash
code-agent experts run bug-fix \
  --log /tmp/ci.log \
  --verify-cmd "pytest -q" \
  --dry-run

code-agent experts run bug-fix \
  --log /tmp/ci.log \
  --verify-cmd "pytest -q" \
  --publish
```

**Parsers:** TypeScript/tsc, ESLint, mypy, Rust, Go, pytest, coverage, Python tracebacks, generic.

**Flow:**

1. Parse log → signals
2. RCA — correlate with git diff + history
3. Build fix task (RCA in MR body)
4. Agent loop + `verify_cmd`
5. Optional publish → branch `ci-fix/<run_id>-<fp>`

| Output | Success | Skipped | Failed |
|--------|---------|---------|--------|
| `status` | `done` | `skipped` | `failed` |
| `signal_count` | ≥ 1 | 0 or duplicate | ≥ 1 |
| `mr_url` | if `--publish` | prior MR if duplicate | — |

**Artifacts:** `signals.json`, `rca.json`, `fix_request.json`, `trace.json`, `diff.patch`

---

## `code-review` — PR inline line comments

| | |
|---|---|
| **When** | First-pass review on a PR diff (nits, bugs, security smells) |
| **Input** | `--pr N` (required) |
| **Output** | One GitHub Review with inline comments (`side=RIGHT`) |
| **Publish** | Comment-only — does **not** open an MR |

```bash
code-agent experts run code-review --pr 42 -w .
code-agent experts run code-review --pr 42 --dry-run -w .   # print findings, no API post
```

Findings: `.code-agent/runs/<run_id>/review-findings.json`. Lines not in the PR diff are skipped. Invalid JSON → exit `2` (fail closed).

---

## `test-intel` — intelligent test selection

| | |
|---|---|
| **When** | Speed up PR CI — run only impacted tests |
| **Input** | Git diff vs `main` (no log required) |

```bash
code-agent experts run test-intel
code-agent experts run test-intel --base-branch main
```

**Does not invoke the coding agent** — produces a test plan only.

| Output | Description |
|--------|-------------|
| `plan.verify_cmd` | e.g. `pytest -q tests/test_foo.py …` |
| `plan.impacted_tests` | Pytest node ids from diff |
| `plan.shards` | Parallel shard groups |
| Artifact | `.code-agent/runs/<run_id>/test_plan.json` |

---

## `deploy-guard` — continuous verification

| | |
|---|---|
| **When** | After deploy / canary — compare metrics to baseline |
| **Input** | `--metrics-file FILE` |

```bash
code-agent experts run deploy-guard \
  --metrics-file metrics/current.json
```

**Metrics JSON:**

```json
{
  "error_rate": 0.01,
  "latency_p99": 110.0,
  "saturation": 0.35
}
```

| Decision | Meaning |
|----------|---------|
| `pass` | No anomalies |
| `block` | Anomaly; no rollback (default) |
| `rollback` | Only with `auto_rollback` + `--confirm-rollback` |

---

## `sre-expert` — incident response

| | |
|---|---|
| **When** | Alertmanager or generic webhook payload |
| **Input** | `--log ALERT.json` |

```bash
code-agent experts run sre-expert \
  --log alert.json \
  --dry-run
```

**Formats:** Alertmanager `{ "alerts": [...] }` or generic `{ "kind": "incident", ... }`.

MR branch prefix: `sre-fix/…`

---

## `monitoring-expert` — observability audit

| | |
|---|---|
| **When** | Weekly audit or pre-release instrumentation check |
| **Input** | None (scans repo) |

```bash
code-agent experts run monitoring-expert --dry-run
```

Finds missing Prometheus/OTel metrics and invalid alert rules.

---

## Shared expert flags

| Flag | Effect |
|------|--------|
| `--dry-run` | No publish; may still write locally |
| `--publish` | Commit + draft MR |
| `--no-artifacts` | Skip `.code-agent/runs/` |
| `-w` | Workspace root |

See [Commands](commands.md) for the full flag list.

---

## CLI commands {#commands}

!!! info "Also on merged page"
    Full content below is preserved. Same section: [features.md#commands](features.md#commands).


Quick reference for every `code-agent` command. For copy-paste workflows see [Recipes](recipes.md).

## Global

```bash
code-agent --help          # or -h — quick starts + examples
code-agent --version       # or -V
code-agent --install-completion   # one-time: tab-complete in your shell
```

| Flag | Effect |
|------|--------|
| `-h`, `--help` | Rich help with examples (works on every subcommand too) |
| `-V`, `--version` | Print `code-agent <version>` and exit |
| `--install-completion` | Install shell completion for the current shell |
| `--show-completion` | Print the completion script (pipe into `eval` / rc file) |
| `--config`, `-c` | Path to `config.yaml` |
| `--workspace`, `-w` | Repo root (default: `.`) |

Mistyped commands get suggestions (e.g. `code-agent docto` → hints `doctor`).

---

## Help & tab completion

The CLI is designed to stay fluid while you type:

1. **Help** — `code-agent -h`, `code-agent run -h`, `code-agent experts run -h` show grouped flags, verify tips, and copy-paste examples.
2. **Tab completion** — after install, complete subcommands, **expert ids**, and common **`--verify-cmd`** values (`pytest -q`, `go test ./...`, …).

### Install completion (once)

=== "bash / zsh / fish (recommended)"

    ```bash
    code-agent --install-completion
    # restart the shell, or open a new terminal
    ```

=== "Current session only"

    ```bash
    eval "$(code-agent --show-completion)"
    ```

=== "Docker (host shell)"

    Completion installs against the **host** `code-agent` binary/PATH entry.  
    If you only use the container image, install a local binary once, or alias:

    ```bash
    alias code-agent='docker run --rm -it -e GEMINI_API_KEY -v "$PWD:/workspace" ghcr.io/kramlipi/code-agent:latest'
    # then: code-agent --install-completion   # if the alias is a real local wrapper script
    ```

### What Tab completes

| You type… | Tab suggests… |
|-----------|----------------|
| `code-agent <TAB>` | `run`, `chat`, `doctor`, `experts`, `web`, `memory`, … |
| `code-agent experts run <TAB>` | `bug-fix`, `test-intel`, `deploy-guard`, `sre-expert`, … |
| `… --verify-cmd <TAB>` | `pytest -q`, `go test ./...`, `npm test`, `mvn test -q`, … |
| `code-agent experts schedule <TAB>` | `flaky-fix`, … |

List experts anytime:

```bash
code-agent experts list
```

---

## `code-agent run` — one-shot task

Fix, add, or refactor code from a natural-language task.

```bash
code-agent run "TASK" [OPTIONS]
```

| Flag | Effect |
|------|--------|
| `--verify-cmd` | Shell command that must exit `0` (tab-completable) |
| `--dry-run` | Plan only; block file writes |
| `--session-id` | Attach to existing session |

**Examples:**

```bash
code-agent run "Add type hints to src/utils.py" -w .
code-agent run "Fix failing login test" --verify-cmd "pytest -q tests/test_auth.py"
code-agent run "Refactor cache module" --dry-run
```

**Success output (shape):**

```text
┌─ Result ─────────────────────────┐
│ Status: done                     │
│ Session: abc123def456            │
│ Run ID: a1b2c3d4e5f6            │
│ Files: src/utils.py              │
└──────────────────────────────────┘
```

---

## `code-agent chat` — interactive REPL

```bash
code-agent chat [-w PATH] [--resume SESSION_ID]
```

Type tasks at `you>` prompt. Type `exit` to quit.

---

## `code-agent doctor` — preflight

```bash
code-agent doctor
code-agent doctor --provider-test
code-agent doctor --verify-plan "fix failing unit tests" -w .
```

Checks Python, ripgrep, config, and optionally pings the LLM provider.

| Flag | Effect |
|------|--------|
| `--provider-test` | Minimal LLM call to validate API key / model |
| `--verify-plan TASK` | Show auto-resolved **SuccessSpec** / verify command for a task (no agent run) |
| `--workspace`, `-w` | Project root for discovery |

**Verify gate:** pass `--verify-cmd` so the agent only finishes when that command exits `0`. See [How to use verify commands](#how-to-use-verify-commands) below.

---

## How to use verify commands

Tell **code-agent** what “done” means with `--verify-cmd`. It edits your repo with tools, then re-runs that command until it exits **0** (or it fails closed).

### See which verify command would be used

No LLM call — discovery only:

```bash
code-agent doctor --verify-plan "fix failing unit tests" -w .
code-agent doctor --verify-plan "increase coverage to 80%" -w .
code-agent doctor --verify-plan "go test the package" -w /path/to/go-project
```

### Fix failing tests (Python)

```bash
cd /path/to/your-python-repo

python3 -m pytest -q   # optional: show red first

code-agent run "Fix all failing unit tests. Minimal changes only — do not change tests unless required." \
  --verify-cmd "python3 -m pytest -q" \
  -w .

python3 -m pytest -q   # same command proves green
```

Narrow the gate:

```bash
code-agent run "Fix the auth tests." \
  --verify-cmd "python3 -m pytest -q tests/test_auth.py" \
  -w .
```

### Fix failing tests (Go)

```bash
cd /path/to/your-go-package

go test ./...

code-agent run "Make unit tests pass. Minimal changes only." \
  --verify-cmd "go test ./..." \
  -w .

go test ./...
```

### Omit `--verify-cmd` (auto-discovery)

If you omit `--verify-cmd`, it tries config → CI → project manifests (`pytest`, `go test`, npm, …). Prefer an **explicit** `--verify-cmd` when you know the right command.

### Docker one-liner

```bash
cd /path/to/your-repo

docker run --rm -it \
  -e GEMINI_API_KEY \
  -e CODE_AGENT_MODEL \
  -v "$PWD:/workspace" \
  ghcr.io/kramlipi/code-agent:latest \
  run "Fix all failing unit tests. Minimal changes only." \
  --verify-cmd "python3 -m pytest -q" \
  -w /workspace
```

For Go, use `--verify-cmd "go test ./..."` (image must have Go, or run the binary locally).

| Tip | Why |
|-----|-----|
| Same verify before and after | Proves the agent actually fixed the failure |
| Keep the prompt tight | “Minimal changes”, “do not weaken other tests” |
| If the run fails | Improve the **prompt**, re-run `code-agent` — don’t hand-edit the fix |
| CI log → fix | `code-agent experts run bug-fix --log fail.log --verify-cmd "…"` |

---

## `code-agent config`

```bash
code-agent config show
```

Prints resolved settings (secrets redacted).

---

## `code-agent env`

```bash
code-agent env sync     # sync keys from host (e.g. Windows geminikey)
code-agent env show     # list discovered keys (redacted)
```

---

## `code-agent experts`

### List experts

```bash
code-agent experts list
```

### Run an expert

```bash
code-agent experts run EXPERT_ID [OPTIONS]
```

| Flag | Effect |
|------|--------|
| `--log FILE` | CI log, alert JSON, or metrics JSON |
| `--run-id ID` | GitHub Actions run id (`bug-fix` only) |
| `--verify-cmd` | Override verification command |
| `--dry-run` | No git publish |
| `--publish` | Commit, push, open draft MR |
| `--approve-publish` | Bypass approval gate |
| `--no-artifacts` | Skip `.code-agent/runs/` |
| `--base-branch` | MR target (default: `main`) |
| `-w`, `--workspace` | Repo root |

### Babysit a PR

```bash
code-agent experts watch --pr NUMBER --verify-cmd "pytest -q"
```

Polls CI on an open PR and runs `bug-fix` when checks fail.

### HTTP serve (platform)

```bash
code-agent experts serve --host 0.0.0.0 --port 8080
```

Webhook router for deploy-guard, budget/throttle, approval gate.

---

## Configuration files

| File | Role |
|------|------|
| `config.yaml` | Model, workspace, expert settings |
| `.env` | API keys (from `env sync`; do not commit) |
| `config.example.yaml` | Template with all options |

**Key settings:**

```yaml
model: gemini/gemini-2.0-flash
workspace: .
max_iterations: 10
temperature: 0.2
```

LiteLLM model strings: `gemini/`, `openai/`, `anthropic/`, `ollama_chat/`, etc.

---

## Outputs

| Location | Contents |
|----------|----------|
| Modified files | In workspace (source/tests) |
| `.code-agent/sessions/` | Chat / run session state |
| `.code-agent/runs/<run_id>/` | Expert artifacts (signals, RCA, trace, diff) |
| Draft MR URL | When `--publish` succeeds |

---

## Related

- [Experts](experts.md) — per-expert inputs and outputs
- [Troubleshooting](troubleshooting.md) — exit codes and common failures

---

## Recipes {#recipes}

!!! info "Also on merged page"
    Full content below is preserved. Same section: [features.md#recipes](features.md#recipes).


Copy-paste commands for common tasks. Replace paths with your project.

!!! tip "Want the why behind each recipe?"
    **[Use Cases](use-cases.md)** explains the pain, command, and benefit for each scenario — start there if you are piloting the agent on your team.

---

## 0. Fluid CLI — help + tab completion

```bash
code-agent -h                          # rich help + examples
code-agent run -h
code-agent experts run -h

code-agent --install-completion        # once per machine
# new terminal:
code-agent experts run <TAB>           # bug-fix, test-intel, …
code-agent run "…" --verify-cmd <TAB>  # pytest -q, go test ./..., …
```

More: [Commands → Help & tab completion](commands.md#help-tab-completion).

---

## A. Fix Python unit tests

```bash
cd ~/karm/ai-code-agent
source .venv/bin/activate

# See failures first
pytest -q

# Option 1: direct run
code-agent run \
  "Fix all failing unit tests in tests/. Run pytest -q after each change until every test passes. Only change test and source code needed for failures — no refactors." \
  --verify-cmd "pytest -q" \
  -w .

# Option 2: bug-fix expert from log
pytest -q 2>&1 | tee /tmp/pytest.log
code-agent experts run bug-fix \
  --log /tmp/pytest.log \
  --verify-cmd "pytest -q" \
  -w .
```

---

## B. Fix Go tests (external repo)

```bash
# See failures
cd /path/to/your-go-project && go test -v ./...

# Option 1: direct run
code-agent run \
  "Fix all failing Go unit tests. Run 'go test -v ./...' after each change until every test passes." \
  --verify-cmd "go test -v ./..." \
  -w /path/to/your-go-project

# Option 2: bug-fix expert
cd /path/to/your-go-project
go test -v ./... 2>&1 | tee /tmp/go-test.log

code-agent experts run bug-fix \
  --log /tmp/go-test.log \
  --verify-cmd "go test -v ./..." \
  -w /path/to/your-go-project
```

!!! warning "Common mistakes"
    - Do **not** use `pytest` for Go projects
    - Use **one** `-w` pointing at the Go repo root

---

## C. Raise code coverage (Python)

```bash
pytest -q --cov=code_agent --cov-report=term-missing --cov-fail-under=80 \
  2>&1 | tee /tmp/coverage-fail.log

code-agent experts run bug-fix \
  --log /tmp/coverage-fail.log \
  --verify-cmd "pytest -q --cov=code_agent --cov-report=term-missing --cov-fail-under=80"
```

See [Coverage](coverage.md) for the full runbook.

---

## D. Run only impacted tests (PR CI)

```bash
code-agent experts run test-intel --base-branch main
# Run the printed verify_cmd in CI
```

---

## E. Babysit a PR until CI green

```bash
code-agent experts watch --pr 42 --verify-cmd "pytest -q"
```

---

## F. Fix from GitHub Actions run

```bash
code-agent experts run bug-fix \
  --run-id 123456789 \
  --verify-cmd "pytest -q" \
  --publish
```

Requires `gh` authenticated and repo access.

---

## G. SRE alert → fix

```bash
code-agent experts run sre-expert \
  --log /path/to/alert.json \
  --verify-cmd "curl -sf http://localhost:8080/health" \
  --dry-run
```

---

## H. Monitoring audit

```bash
code-agent experts run monitoring-expert --dry-run
```

---

## I. Dry run (no writes)

```bash
code-agent run "Refactor error handling" --dry-run -w .
code-agent experts run bug-fix --log /tmp/ci.log --dry-run
```

---

## J. Interactive chat on a project

```bash
code-agent chat -w /path/to/project
# type tasks; exit with: exit

code-agent chat --resume SESSION_ID -w /path/to/project
```

---

## Prompt templates

**Minimal fix:**

```text
Fix the failing tests. Run VERIFY_CMD after each change. Minimal diff only.
```

**Add feature + test:**

```text
Add FEATURE. Add a test. Match existing code style. Run VERIFY_CMD until green.
```

**Coverage:**

```text
Raise line coverage to THRESHOLD%. Add unit tests under tests/ for uncovered lines.
Do not delete production code. Do not edit .github/workflows.
```

---

## Coverage {#coverage}

!!! info "Also on merged page"
    Full content below is preserved. Same section: [features.md#coverage](features.md#coverage).


Runbook for raising line coverage on Python projects (especially `code_agent`).

!!! tip "Why raise coverage with the agent?"
    See [Use Cases → Coverage gate blocking merge](use-cases.md#4-coverage-gate-blocking-merge) for the full why → command → benefit flow.

## Baseline commands

```bash
pip install -e ".[dev]"

# All tests
pytest -q

# Coverage report with missing lines
pytest -q --cov=code_agent --cov-report=term-missing

# PR gate (fails if below 80%)
pytest -q --cov=code_agent --cov-report=term-missing --cov-fail-under=80
```

**Expected when below gate:**

```text
FAIL Required test coverage of 80% not reached. Total coverage: 68.xx%
```

Exit code: `1`

## HTML report

```bash
pytest -q --cov=code_agent --cov-report=html
# open htmlcov/index.html
```

## One-module loop (fast iteration)

```bash
pytest -q tests/test_tools_files.py \
  --cov=code_agent.tools.files \
  --cov-report=term-missing \
  --cov-fail-under=0
```

Read the `Missing` column — those line numbers need tests.

## Agent-assisted coverage fix

```bash
pytest -q --cov=code_agent --cov-report=term-missing --cov-fail-under=80 \
  2>&1 | tee /tmp/coverage-fail.log

code-agent experts run bug-fix \
  --log /tmp/coverage-fail.log \
  --verify-cmd "pytest -q --cov=code_agent --cov-report=term-missing --cov-fail-under=80"
```

The agent is instructed to **add tests**, not delete production code or edit CI YAML.

## Test conventions

| Rule | Detail |
|------|--------|
| Location | `tests/test_<module>.py` |
| Style | Plain pytest; `tmp_path` for filesystem |
| External I/O | Mock subprocess, network, LLM |
| Assertions | Behavior over implementation |

## Priority backlog (code_agent)

| Priority | Module | Suggested test file |
|----------|--------|---------------------|
| P0 | `tools/git_utils.py` | `tests/test_git_utils.py` |
| P0 | `rag.py` | `tests/test_rag.py` |
| P1 | `publish/git_ops.py` | `tests/test_publish_git_ops.py` |
| P1 | `publish/mr_creator.py` | `tests/test_publish_mr_creator.py` |
| P2 | `cli.py` | `tests/test_cli_*.py` (Typer CliRunner) |

## Anti-patterns

- Deleting hard-to-test code to raise %
- Lowering `fail-under` in CI without team agreement
- Committing `htmlcov/`, `.coverage`, `coverage.json`

## Definition of done

1. `pytest -q` exits `0`
2. `--cov-fail-under=80` exits `0` (or agreed threshold)
3. New tests under `tests/`
4. No `.github/workflows/**` changes