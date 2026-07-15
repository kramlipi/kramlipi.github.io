---
title: Early Adopter Use Cases
description: >-
  Real-world ways to use code-agent in CI and development — why, command, and
  benefit for each scenario. Written for teams piloting the agent today.
keywords: code-agent use cases, ci automation, early adopter, devops, test coverage, telemetry
---

# Early Adopter Use Cases

You are not buying a chatbot. You are adding a **verify-gated automation worker** that reads logs, edits your repo, and proves fixes with the same command CI uses.

**Pain index:** [Developer & DevOps pains](pains.md) — every pain we target, what “fixed” means, and the first command to try.

Every example below follows the same pattern:

| | |
|---|---|
| **Why** | The pain you have right now |
| **Command** | What to run (copy-paste) |
| **Benefit** | What you get back — time, safety, or signal |

!!! tip "Early adopter mindset"
    Start with **`--dry-run`** or local runs without `--publish`.  
    Add `--publish` only after you trust verify commands on one repo.

---

## 1. CI failed — you need a fix tonight

### 1.1 GitHub Actions log → fix → re-run tests

**Why:** CI failed at 11pm. The log is 3,000 lines. You know *something* in `auth/` broke but do not want to read every stack frame.

**Command:**

```bash
# Save the failed run log (or use --run-id from GitHub)
gh run view 123456789 --log-failed 2>&1 | tee /tmp/ci.log

code-agent experts run bug-fix \
  --log /tmp/ci.log \
  --verify-cmd "pytest -q" \
  -w /path/to/your-repo
```

**Benefit:** Parser extracts file/line/errors → agent fixes only what the log needs → `pytest -q` must pass before it stops. You review a small diff, not the whole log.

---

### 1.2 Open a draft PR so morning review is easy

**Why:** You want the fix on a branch with RCA in the description — not a Slack paste of "I think it's auth.py".

**Command:**

```bash
code-agent experts run bug-fix \
  --log /tmp/ci.log \
  --verify-cmd "pytest -q" \
  -w /path/to/your-repo \
  --publish \
  --base-branch main
```

**Benefit:** Draft MR with evidence-based RCA, scoped diff, verify already run. Senior reviews architecture; agent did triage.

---

### 1.3 TypeScript / ESLint / mypy failures (not just pytest)

**Why:** Polyglot repo — CI runs `tsc`, ESLint, and pytest. Same agent, different parsers.

**Command:**

```bash
npm run build 2>&1 | tee /tmp/ci.log

code-agent experts run bug-fix \
  --log /tmp/ci.log \
  --verify-cmd "npm run build && npm test" \
  -w /path/to/your-repo
```

**Benefit:** One intake path for compiler, lint, and test failures. Verify command matches *your* CI gate.

---

## 2. Slow CI — stop running the full suite

### 2.1 PR only touched two files — run impacted tests

**Why:** Full suite is 40 minutes. Your PR changed one module. Running 2,000 tests wastes money and blocks merge.

**Command:**

```bash
cd /path/to/your-repo

code-agent experts run test-intel --base-branch main
# Copy the printed verify_cmd into CI or run locally:
# pytest -q tests/test_auth.py tests/test_login.py
```

**Benefit:** Git diff → pytest node list → shell command you paste into PR CI. Early adopters often cut PR feedback from hours to minutes.

---

### 2.2 Wire test-intel into GitHub Actions before pytest

**Why:** You want CI to *always* run the selective command, not full suite on every push.

**Command (local plan first):**

```bash
code-agent experts run test-intel --base-branch main > /tmp/plan.txt
cat .code-agent/runs/*/test_plan.json
```

**Benefit:** Artifact `test_plan.json` documents *why* those tests were chosen. Platform team can gate: if plan is empty, fall back to full suite.

---

## 3. Failing unit tests — by language

### 3.1 Python — pytest red on your feature branch

**Why:** You merged `main` and 4 tests fail. You care about shipping, not archaeology.

**Command:**

```bash
cd /path/to/your-repo
pytest -q 2>&1 | tee /tmp/pytest.log

code-agent experts run bug-fix \
  --log /tmp/pytest.log \
  --verify-cmd "pytest -q" \
  -w .
```

**Benefit:** Minimal diff; tests green; no manual "fix test_foo, run pytest, repeat" loop.

[Full Python walkthrough →](examples/python.md)

---

### 3.2 Go — `go test` failed after refactor

**Why:** Renamed a package; three `_test.go` files still import the old path.

**Command:**

```bash
cd /path/to/your-go-service
go test -v ./... 2>&1 | tee /tmp/go.log

code-agent experts run bug-fix \
  --log /tmp/go.log \
  --verify-cmd "go test -v ./..." \
  -w .
```

**Benefit:** Go parser + verify with `go test` — not pytest by mistake.

[Full Go walkthrough →](examples/go.md)

---

### 3.3 Java — Maven surefire failure on PR

**Why:** Spring service test fails after DTO change; stack trace is buried in Maven output.

**Command:**

```bash
mvn test -q 2>&1 | tee /tmp/maven.log

code-agent experts run bug-fix \
  --log /tmp/maven.log \
  --verify-cmd "mvn test -q" \
  -w /path/to/java-project
```

**Benefit:** Agent reads surefire output; adds/fixes tests under `src/test/java/`. Verify uses the same Maven command CI uses.

[Full Java walkthrough →](examples/java.md)

---

## 4. Coverage gate blocking merge

### 4.1 CI fails: "Required test coverage of 80% not reached"

**Why:** Sonar or pytest-cov blocks merge. You need *tests*, not a debate about lowering the gate.

**Command:**

```bash
pytest -q --cov=my_package --cov-report=term-missing --cov-fail-under=80 \
  2>&1 | tee /tmp/cov.log

code-agent experts run bug-fix \
  --log /tmp/cov.log \
  --verify-cmd "pytest -q --cov=my_package --cov-report=term-missing --cov-fail-under=80" \
  -w /path/to/your-repo
```

**Benefit:** Agent is instructed to **add tests**, not delete production code. Coverage rises; gate passes objectively.

[Coverage runbook →](coverage.md)

---

### 4.2 New module shipped with zero tests

**Why:** Feature merged fast; coverage dropped 5%. Compliance wants tests before next release.

**Command:**

```bash
code-agent run \
  "Add unit tests for src/my_package/new_feature.py. Cover happy path and one error path. Match existing test style in tests/. Do not change production logic unless required for testability." \
  --verify-cmd "pytest -q --cov=my_package --cov-fail-under=80" \
  -w /path/to/your-repo
```

**Benefit:** Prompt mode when there is no CI log yet — still verify-gated.

---

## 5. Flaky or repeated CI failures

### 5.1 Same PR keeps failing — babysit until green

**Why:** You opened PR #42; CI fails, you fix, push, fails again on a different test. You have other work.

**Command:**

```bash
code-agent experts watch \
  --pr 42 \
  --verify-cmd "pytest -q" \
  -w /path/to/your-repo
```

**Benefit:** Watcher polls CI → runs `bug-fix` on new failures → pushes fixes to the PR branch (with `--publish`, default on). You get notified when green.

!!! note "Honest limit"
    code-agent does **not** yet classify "this test is flaky" vs "real bug" from history alone.  
    It fixes the **current** failure with RCA + dedup (same fingerprint in 24h → skip duplicate MR).

---

### 5.2 Duplicate auto-fix MRs cluttering the repo

**Why:** CI flaps; bot opens five identical MRs overnight.

**Command:** (no extra flags — built-in)

```bash
code-agent experts run bug-fix --log /tmp/ci.log --verify-cmd "pytest -q" -w .
# Second identical run within 24h → status: skipped (duplicate fingerprint)
```

**Benefit:** Dedup by failure fingerprint. Early adopters avoid MR spam while iterating on pipeline wiring.

---

## 6. Missing telemetry and observability

### 6.1 Audit repo before release — find handlers without metrics

**Why:** Production readiness review asks "do all HTTP routes export latency?" Manual grep does not scale.

**Command:**

```bash
code-agent experts run monitoring-expert \
  -w /path/to/your-repo \
  --dry-run
```

**Benefit:** Scan finds `missing_metric`, bad Prometheus rules, SLO gaps. Report in `.code-agent/runs/` — no code changes until you are ready.

---

### 6.2 Open MR that adds Prometheus / OTel instrumentation

**Why:** Audit found 12 routes without metrics. You want a draft PR, not a Jira ticket that sits for a sprint.

**Command:**

```bash
code-agent experts run monitoring-expert \
  -w /path/to/your-repo \
  --publish
```

**Benefit:** Branch + draft MR with instrumentation changes. Human reviews; agent did the boring scan + first pass.

---

## 7. SRE and incidents

### 7.1 Alertmanager webhook — reliability fix, not kubectl roulette

**Why:** `HighErrorRate` fired. Logs show timeout to downstream API. You want retry/config fix in *code*, not a manual prod shell session.

**Command:**

```bash
code-agent experts run sre-expert \
  --log /path/to/alert.json \
  --verify-cmd "curl -sf http://localhost:8080/health" \
  -w /path/to/your-repo \
  --dry-run
```

**Benefit:** Alert → structured intake → fix focused on timeouts/retries/config. Verify is your health check, not LLM opinion.

---

### 7.2 Post-deploy — metrics look wrong, block or pass

**Why:** Canary deployed. Error rate ticked up 0.5%. You need an automated compare to baseline before full rollout.

**Command:**

```bash
code-agent experts run deploy-guard \
  --metrics-file metrics/current.json \
  -w /path/to/your-repo
```

**Benefit:** Decision artifact: `pass`, `block`, or `rollback` (dry-run by default). Early adopters use this as a gate *after* deploy hooks.

---

## 8. Platform / DevEx team — one agent, many repos

### 8.1 Golden path: any repo, same command

**Why:** You support 50 microservices. Engineers should not learn a different fix ritual per repo.

**Command (document in internal wiki):**

```bash
export REPO=/path/to/service
pytest -q 2>&1 | tee /tmp/ci.log
code-agent experts run bug-fix \
  --log /tmp/ci.log \
  --verify-cmd "pytest -q" \
  -w "$REPO"
```

**Benefit:** Same expert, same flags, same exit codes (`0`/`1`/`2`) everywhere. Platform owns `config.yaml` templates per language.

---

### 8.2 HTTP service for webhooks (deploy-guard, future CI hooks)

**Why:** GitLab/GitHub webhooks should trigger experts without SSH to a builder.

**Command:**

```bash
code-agent experts serve --host 0.0.0.0 --port 8787 -w /path/to/platform-checkout
```

**Benefit:** Router + budget/throttle + approval gate (see product `config.yaml`). Early adopters run this in k8s or Docker Compose behind auth.

[Docker / container quick start →](quick-start.md)

---

### 8.3 Docker — no pip install on developer laptops

**Why:** Security policy blocks local Python installs. Devs still need the agent against mounted repos.

**Command:**

```bash
docker pull ghcr.io/kramlipi/code-agent:latest

docker run --rm -it \
  -e GEMINI_API_KEY \
  -v "$PWD:/workspace" \
  ghcr.io/kramlipi/code-agent:latest \
  experts run bug-fix \
  --log /workspace/ci.log \
  --verify-cmd "pytest -q" \
  -w /workspace
```

**Benefit:** Same CLI, ripgrep + git inside image. Workspace is always `/workspace` — fits locked-down laptops and CI runners.

---

## 9. Automated PR line comments (code-review)

### 9.1 First-pass review on every pull request

**Why (SEO intent):** “How do I get automated PR code review comments on changed lines?” Manual review misses nits; full senior review doesn’t scale.

**Pain:** PRs merge with bugs, hardcoded secrets, or broken APIs that a quick diff pass would catch.

**How we solve it:** LLM reviews the **PR unified diff**, writes structured findings (`path` + `line`), filters to lines that exist on the RIGHT side of the diff, and posts **one GitHub Review** with inline comments via `gh api`. Comment-only — no auto-fix, no MR.

**Command:**

```bash
export GH_TOKEN=...   # or GITHUB_TOKEN in Actions
export GEMINI_API_KEY=...
export CODE_AGENT_MODEL=gemini/gemini-2.0-flash
```

# Preview findings without posting:
code-agent experts run code-review --pr 42 --dry-run -w /path/to/your-repo
```

**Benefit:** File:line comments on the PR. Invalid findings JSON fails closed (exit `2`). Lines not in the diff are skipped.

### 9.2 Wire into CI (GitHub / GitLab / Azure)

**Why:** Every PR/MR should get a first-pass without a human clicking “run”.

**Copy-paste YAML:** **[Code review CI](code-review-ci.md)** — GitHub Actions (inline comments), GitLab CI, Azure Pipelines.

**GitHub Actions (inline):**

```yaml
- run: |
    code-agent experts run code-review \
      --pr ${{ github.event.pull_request.number }} \
      -w .
  env:
    GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
    CODE_AGENT_MODEL: gemini/gemini-3.1-flash-lite
```

**GitLab / Azure (diff file):**

```bash
git diff origin/main...HEAD > /tmp/mr.diff
code-agent experts run code-review --diff-file /tmp/mr.diff -w .
```

**Benefit:** Same binary from [Releases](https://github.com/kramlipi/code-agent-binaries/releases). Economy mode off by default.

---

## 10. Day-one developer workflows

### 10.1 "Just fix this one file" — ad-hoc task

**Why:** Lint rule added; 50 files flagged. You only care about `utils.py` today.

**Command:**

```bash
code-agent run \
  "Fix all mypy errors in src/utils.py only. Do not touch other files." \
  --verify-cmd "mypy src/utils.py" \
  -w .
```

**Benefit:** Scoped prompt + scoped verify. Agent cannot claim done if mypy still fails.

---

### 10.2 Explore safely — dry run before writes

**Why:** You want to see what the agent *would* change before trusting it on `main`.

**Command:**

```bash
code-agent run \
  "Plan fixes for failing tests in tests/test_api.py" \
  --verify-cmd "pytest -q tests/test_api.py" \
  --dry-run \
  -w .
```

**Benefit:** Plans and tool calls without file writes. Good first step for security review.

---

### 10.3 Multi-turn session on a hard bug

**Why:** One-shot failed; you need to steer ("also check the mock fixture").

**Command:**

```bash
code-agent chat -w /path/to/your-repo
# you> Fix test_login_invalid_password
# you> The mock for redis is wrong — see tests/conftest.py
# you> exit
```

**Benefit:** Session persisted under `.code-agent/sessions/`. Resume with `--resume SESSION_ID`.

---

## 11. What early adopters should NOT expect (yet)

| Wish | Reality today | What to do instead |
|------|---------------|-------------------|
| "Replace a senior design review" | Ships nits/bugs/security smells as **line comments**, not architecture sign-off | Use `code-review` for first pass; humans for design |
| "Mark test as flaky automatically" | No flake scorer | Use `bug-fix` + human triage |
| "Edit GitHub Actions to make green" | **Blocked** by safety policy | Fix app code/tests |
| "100% correct first try" | Bounded by `max_iterations` | Tighten `--verify-cmd`; use `--dry-run` first |
| "Replace staging environment" | Agent edits code; does not deploy | Pair with `deploy-guard` metrics gate |

---

## 12. Quick picker — which command for my pain?

| I need to… | Start here |
|------------|------------|
| Increase code coverage | `run "increase unit test coverage" --verify-cmd …` |
| Fix CI / broken build from a log | `experts run bug-fix --log …` |
| PR inline review comments | `experts run code-review --pr N` |
| Run fewer tests on PR | `experts run test-intel` |
| Raise coverage from cov log | `bug-fix` on coverage log or [Coverage](coverage.md) |
| PR keeps failing overnight | `experts watch --pr N` |
| Find missing metrics | `experts run monitoring-expert` |
| MR for telemetry | `monitoring-expert --publish` |
| Alert → code fix | `experts run sre-expert --log alert.json` |
| Post-deploy metric check | `experts run deploy-guard` |
| Try without installing Python | Binary [Drive](https://drive.google.com/drive/folders/11iuNWM13SjrlKastaA_2FaMz4tGg9_QX?usp=sharing) or `docker run … ghcr.io/kramlipi/code-agent` |
| Learn all flags | [Commands](commands.md) |
| Copy-paste only | [Recipes](recipes.md) |

---

## 13. Suggested 2-week pilot (one team)

| Week | Action | Success metric |
|------|--------|----------------|
| 1 | Binary + `doctor` + one `bug-fix --dry-run` on real CI log | Verify exits 0 locally |
| 1 | `code-review --dry-run` on an open PR | Findings look sane |
| 1 | `test-intel` on 3 PRs | Compare time vs full suite |
| 2 | `bug-fix --publish` on one failing PR | Draft MR merged with human review |
| 2 | `code-review` in Actions (no dry-run) | Inline comments on PR |
| 2 | `monitoring-expert --dry-run` before release | List of metric gaps documented |

---

## Related docs

- [Pains catalog](pains.md) — developer + DevOps pains → use cases
- [Home / Quick start](index.md) — binary first, then commands
- [Quick Start](quick-start.md) — install and first command
- [Experts](experts.md) — inputs/outputs per expert
- [Recipes](recipes.md) — copy-paste commands without narrative
- [Coverage](coverage.md) — pytest-cov runbook
- [Troubleshooting](troubleshooting.md) — exit codes and failures
