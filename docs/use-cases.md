---
title: Use cases
description: >-
  Real-world ways to use code-agent — pains, symptoms, solutions, commands,
  language walkthroughs, and early-adopter playbooks. Nothing removed.
keywords: code-agent use cases, ci automation, pains, python go java examples
---

# Use cases

Pick your **symptom** below, then scroll for the full playbooks, pain catalog, and language examples.

## Symptoms at a glance {#symptoms}

<div class="kl-symptom-grid" markdown="0">
  <div class="kl-symptom-card">
    <span class="kl-symptom-label">CI red at midnight</span>
    <p>3,000-line log. You need green before morning.</p>
    <a href="#1-ci-failed--you-need-a-fix-tonight">Fix CI →</a>
  </div>
  <div class="kl-symptom-card">
    <span class="kl-symptom-label">Coverage gate blocks merge</span>
    <p>80% not reached. You need tests, not a weaker gate.</p>
    <a href="#4-coverage-gate-blocking-merge">Raise coverage →</a>
  </div>
  <div class="kl-symptom-card">
    <span class="kl-symptom-label">No first-pass PR review</span>
    <p>Bugs and nits slip through. Seniors can't scale.</p>
    <a href="#9-automated-pr-line-comments-code-review">Review PR →</a>
  </div>
  <div class="kl-symptom-card">
    <span class="kl-symptom-label">Full suite on every tiny PR</span>
    <p>40-minute CI. One file changed.</p>
    <a href="#2-slow-ci--stop-running-the-full-suite">Run fewer tests →</a>
  </div>
  <div class="kl-symptom-card">
    <span class="kl-symptom-label">Ops: alerts, metrics, flapping PR</span>
    <p>PagerDuty, missing telemetry, PR keeps failing.</p>
    <a href="#6-missing-telemetry-and-observability">Ops &amp; platform →</a>
  </div>
</div>

!!! tip "Five jobs, one page"
    **Symptom → solution → command** in the sections below.  
    Full pain catalog: [Pains catalog](#pains-catalog) · Python/Go/Java: [Language walkthroughs](#language-walkthroughs)

---

## Early adopter playbooks {#playbooks}

Pick your **symptom** below, then scroll for the full playbooks, pain catalog, and language examples.

## Symptoms at a glance {#symptoms}

<div class="kl-symptom-grid" markdown="0">
  <div class="kl-symptom-card">
    <span class="kl-symptom-label">CI red at midnight</span>
    <p>3,000-line log. You need green before morning.</p>
    <a href="#1-ci-failed--you-need-a-fix-tonight">Fix CI →</a>
  </div>
  <div class="kl-symptom-card">
    <span class="kl-symptom-label">Coverage gate blocks merge</span>
    <p>80% not reached. You need tests, not a weaker gate.</p>
    <a href="#4-coverage-gate-blocking-merge">Raise coverage →</a>
  </div>
  <div class="kl-symptom-card">
    <span class="kl-symptom-label">No first-pass PR review</span>
    <p>Bugs and nits slip through. Seniors can't scale.</p>
    <a href="#9-automated-pr-line-comments-code-review">Review PR →</a>
  </div>
  <div class="kl-symptom-card">
    <span class="kl-symptom-label">Full suite on every tiny PR</span>
    <p>40-minute CI. One file changed.</p>
    <a href="#2-slow-ci--stop-running-the-full-suite">Run fewer tests →</a>
  </div>
  <div class="kl-symptom-card">
    <span class="kl-symptom-label">Ops: alerts, metrics, flapping PR</span>
    <p>PagerDuty, missing telemetry, PR keeps failing.</p>
    <a href="#6-missing-telemetry-and-observability">Ops &amp; platform →</a>
  </div>
</div>

!!! tip "Five jobs, one page"
    **Symptom → solution → command** in the sections below.  
    Full pain catalog: [Pains catalog](#pains-catalog) · Python/Go/Java: [Language walkthroughs](#language-walkthroughs)

---

## Early adopter playbooks {#playbooks}

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

---

## Developer & DevOps pains catalog {#pains-catalog}

These are the pains teams already feel. Each use case says what **fixed** looks like and which command to try. Every fix path is **verify-gated**: your command must exit `0` — the model does not get to declare success alone.

For narrative walkthroughs see [Use Cases](use-cases.md). For flags see [Commands](commands.md).

---

## Developer pains

### Unreadable CI log at 11pm

**Pain:** Thousands of log lines; Slack archaeology; nobody knows if it’s a flake or your PR.  
**Fixed when:** Failure is parsed → scoped fix → **same** verify command exits `0` → optional draft PR with RCA.

```bash
gh run view <RUN_ID> --log-failed > ci.log
code-agent experts run bug-fix \
  --log ci.log --verify-cmd "pytest -q" -w . --publish
```

---

### Passes locally, fails in CI

**Pain:** Green laptop, red pipeline (env, versions, missing services).  
**Fixed when:** You run the agent with the **exact** CI verify command (often in the official container).

```bash
docker run --rm -it -e GEMINI_API_KEY -v "$PWD:/workspace" \
  ghcr.io/kramlipi/code-agent:latest \
  experts run bug-fix --log /workspace/ci.log \
  --verify-cmd "pytest -q" -w /workspace
```

---

### Full suite on every tiny PR

**Pain:** One-file change waits 40+ minutes; CI cost and merge queue pain.  
**Fixed when:** Diff → impacted tests → selective verify command (fallback to full suite when unsure).

```bash
code-agent experts run test-intel --base-branch main -w .
```

---

### Coverage gate blocks merge

**Pain:** “80% not reached”; temptation to weaken the gate.  
**Fixed when:** Agent **adds tests**; coverage command still exits `0`.

```bash
code-agent run \
  "Add unit tests for src/pkg/new_feature.py. Match tests/ style." \
  --verify-cmd "pytest -q --cov=pkg --cov-fail-under=80" -w .
```

---

### No first-pass PR review on every change

**Pain:** PRs merge with obvious bugs, secrets, or broken APIs; senior review doesn’t scale.  
**Fixed when:** Automated **inline comments** on the PR diff (comment-only); humans still own design sign-off.

```bash
code-agent experts run code-review --pr 42 -w .
code-agent experts run code-review --pr 42 --dry-run -w .
```

---

### Same PR fails again and again

**Pain:** Fix → push → new failure → all-day context switch.  
**Fixed when:** Watcher polls checks and re-runs the fix loop until green or max attempts.

```bash
code-agent experts watch --pr 42 --verify-cmd "pytest -q" -w .
```

---

### Flaky tests burn trust

**Pain:** Random red; people re-run until green; real bugs hide.  
**Fixed when:** Known flaky tests can be skipped in selective plans **with a report**; current failures still get fixed.  
**Honest limit:** Strong statistical flake scoring is not shipped yet — use `bug-fix` on the **current** failure and human quarantine for chronic flakes.

---

### Lint / type / format debt after a rule change

**Pain:** New mypy/ruff/eslint rule; hundreds of files; merge blocked on style.  
**Fixed when:** Narrow verify is green; edits stay scoped.

```bash
code-agent run "Fix mypy errors in src/utils.py only." \
  --verify-cmd "mypy src/utils.py" -w .
```

---

### Unfamiliar repo — where do I start?

**Pain:** New hire / rotation; failing tests; fear of breaking main.  
**Fixed when:** Doctor shows which verify would run; chat/UI can explore; dry-run before writes.

```bash
code-agent doctor --verify-plan "fix failing unit tests" -w .
code-agent chat -w .
```

---

### Dependency / Dependabot PR is red

**Pain:** Version bump breaks callers; bot PR sits red for weeks.  
**Fixed when:** Failed upgrade CI log → app/adapter fix → verify green → human merge.

```bash
code-agent experts run bug-fix \
  --log /tmp/dependabot-ci.log \
  --verify-cmd "pytest -q" -w .
```

---

### AI claimed “fixed” without proof

**Pain:** Chatbots invent success; trust collapses.  
**Fixed when:** Agent cannot finish successfully unless your verify subprocess exits `0`.

```bash
code-agent run "Fix failing unit tests" --verify-cmd "pytest -q" -w .
```

---

### Refactor left broken imports

**Pain:** Rename/package move; tests and callers lag.  
**Fixed when:** Language verify (`pytest`, `go test`, `mvn test`, …) exits `0`.

See [Python](examples/python.md) · [Go](examples/go.md) · [Java](examples/java.md).

---

## DevOps / platform / SRE pains

### Platform is the eternal CI babysitter

**Pain:** Every team pings platform to read logs.  
**Fixed when:** One golden-path command works on every service (same exit codes).

```bash
code-agent experts run bug-fix --log ci.log --verify-cmd "pytest -q" -w "$REPO"
```

---

### CI minutes / runner cost explode

**Pain:** Full suites on every push; finance asks why the bill doubled.  
**Fixed when:** Selective tests on PRs via `test-intel`; org workflow template.

```bash
code-agent experts run test-intel --base-branch main -w .
```

---

### Flapping pipelines → duplicate bot PRs

**Pain:** Overnight spam of identical “fix” MRs.  
**Fixed when:** Dedup by failure fingerprint (same failure within TTL → skip).

Built into `bug-fix` — no extra flags.

---

### Agents must not cheat CI

**Pain:** Fear that AI will edit workflows or disable checks to go green.  
**Fixed when:** Forbidden paths (e.g. `.github/workflows`) enforced; review the draft MR.

---

### Missing metrics / SLO before release

**Pain:** Readiness asks for latency/error metrics; manual grep does not scale.  
**Fixed when:** Scan → gap report; optional draft MR with instrumentation.

```bash
code-agent experts run monitoring-expert -w . --dry-run
code-agent experts run monitoring-expert -w . --publish
```

---

### Alert fired — kubectl roulette

**Pain:** PagerDuty noise; tribal knowledge; manual prod edits.  
**Fixed when:** Alert → code/config remediations → health verify → draft MR (start with `--dry-run`).

```bash
code-agent experts run sre-expert \
  --log ./alert.json \
  --verify-cmd "curl -sf http://localhost:8080/health" \
  -w . --dry-run
```

---

### Post-deploy — is the canary safe?

**Pain:** Metrics tick up; nobody owns go/no-go.  
**Fixed when:** Compare to baseline → `pass` / `block` / `rollback` artifact.

```bash
code-agent experts run deploy-guard --metrics-file metrics/current.json -w .
```

---

### Webhooks should trigger experts (no SSH)

**Pain:** Events need HTTP intake; jump hosts do not scale.  
**Fixed when:** `experts serve` behind auth with budget/throttle gates.

```bash
code-agent experts serve --host 0.0.0.0 --port 8787 -w /path/to/checkout
```

---

### Locked-down laptops (no local pip)

**Pain:** Security blocks local Python installs.  
**Fixed when:** Official image + mounted workspace.

```bash
docker pull ghcr.io/kramlipi/code-agent:latest
# see Quick Start for docker-ui.sh
```

---

### Nightly job red for days

**Pain:** Scheduled pipeline fails unnoticed until Monday.  
**Fixed when:** On `failure()`, run `bug-fix` → draft MR + notify (wire in Actions/GitLab).

---

### Compliance — what did the bot change?

**Pain:** SOC2 / customer asks for an audit trail.  
**Fixed when:** Every run leaves artifacts under `.code-agent/runs/` (signals, verify, diff).

---

## What we are not (yet)

| Pain | Reality |
|------|---------|
| “Review every PR like a senior” | We babysit **CI green**, not design review |
| “Auto-mark flaky and forget” | No strong flake scorer yet — fix current failure; quarantine by policy |
| “Edit workflows to make green” | **Blocked** by safety |
| “Fix Terraform/Helm as a first-class expert” | Use custom `--verify-cmd` today; dedicated IaC path is later |
| “Replace staging / kubectl” | Agent edits **code**; pair with `deploy-guard` for metrics gates |

---

## Quick picker

| I need to… | Start here |
|------------|------------|
| Fix CI from a log | `experts run bug-fix --log …` |
| Run fewer tests on a PR | `experts run test-intel` |
| Raise coverage | `run` / `bug-fix` + cov verify |
| Babysit a flapping PR | `experts watch --pr N` |
| Find missing metrics | `experts run monitoring-expert` |
| Alert → code fix | `experts run sre-expert` |
| Post-deploy metrics gate | `experts run deploy-guard` |
| Prove “done” | always `--verify-cmd` |
| No local Python | Docker / [Quick Start](quick-start.md) |

---

## Related

- [Early adopter use cases](use-cases.md) — why / command / benefit in depth  
- [Recipes](recipes.md) — copy-paste only  
- [Experts](experts.md) — inputs and outputs  
- [Commands](commands.md) — CLI reference including verify how-to  

---

## Language walkthroughs {#language-walkthroughs}

### Python — failing unit tests {#python-example}

## What do you want?

| Goal | Command |
|------|---------|
| **Fix a broken build / failing pytest** | `code-agent experts run bug-fix --log /tmp/ci.log --verify-cmd "pytest -q" -w .` |
| **Increase coverage** | `code-agent run "increase unit test coverage" --verify-cmd "pytest -q --cov=PKG --cov-fail-under=80" -w .` |
| **PR line review** | `code-agent experts run code-review --pr N -w .` |

End-to-end below: **create a failing test → fix with code-agent**.

Home quick start (binary first): [Get started](../get-started.md) · [Use cases](../use-cases.md)

---

## 1. Create a failing test (in your repo)

```bash
mkdir -p /tmp/py-demo && cd /tmp/py-demo
git init

# Minimal package
mkdir -p myapp tests
cat > myapp/__init__.py <<'EOF'
def add(a: int, b: int) -> int:
    return a + b
EOF

cat > myapp/calc.py <<'EOF'
def add(a: int, b: int) -> int:
    return a - b   # BUG: should be +
EOF

cat > tests/test_calc.py <<'EOF'
from myapp.calc import add

def test_add():
    assert add(2, 3) == 5
EOF

pip install pytest
pytest -q
```

**Expected (failure):**

```text
FAILED tests/test_calc.py::test_add - assert -1 == 5
1 failed
```

**Save the log:**

```bash
pytest -q 2>&1 | tee /tmp/pytest.log
```

---

## 2. Fix with `code-agent run` (prompt mode)

```bash
source /path/to/ai-code-agent/.venv/bin/activate

code-agent run \
  "Fix the failing test in tests/test_calc.py. The add() function in myapp/calc.py is wrong. Run pytest -q until all tests pass. Change only what is needed." \
  --verify-cmd "pytest -q" \
  -w /tmp/py-demo
```

### Flags explained

| Flag | Value | Meaning |
|------|-------|---------|
| `"..."` | task text | What you want — plain English |
| `--verify-cmd` | `pytest -q` | Agent must run this and get exit `0` before finishing |
| `-w` | `/tmp/py-demo` | **Workspace** — only this repo is edited |

**Expected:**

```text
Status: done
Files: myapp/calc.py
```

**Verify yourself:**

```bash
cd /tmp/py-demo && pytest -q
# 1 passed
```

---

## 3. Fix with `bug-fix` expert (CI log mode)

Best when CI already failed and you have a log file.

```bash
cd /tmp/py-demo
pytest -q 2>&1 | tee /tmp/pytest.log

code-agent experts run bug-fix \
  --log /tmp/pytest.log \
  --verify-cmd "pytest -q" \
  -w /tmp/py-demo
```

### Flags explained

| Flag | Meaning | Why use it |
|------|---------|------------|
| `--log` | Path to pytest output | Expert **parses** failures (file, line, assertion) — no guessing |
| `--verify-cmd` | Must match what CI runs | Same proof as GitHub Actions |
| `-w` | Your Python repo | Agent edits `myapp/` and `tests/` here |
| `--dry-run` | (optional) Try without publish | First safe run |
| `--publish` | (optional) Open draft PR | After local verify works |

**Parser support:** pytest failures, coverage failures, Python tracebacks, mypy.

---

## 4. Raise coverage (add missing unit tests)

Break coverage on purpose:

```bash
cat >> myapp/calc.py <<'EOF'

def multiply(a: int, b: int) -> int:
    return a * b
EOF

# No test for multiply yet
pytest -q --cov=myapp --cov-report=term-missing --cov-fail-under=80 2>&1 | tee /tmp/cov.log
```

Fix:

```bash
code-agent experts run bug-fix \
  --log /tmp/cov.log \
  --verify-cmd "pytest -q --cov=myapp --cov-report=term-missing --cov-fail-under=80" \
  -w /tmp/py-demo
```

Agent adds tests in `tests/` — does **not** remove `multiply()` to cheat.

---

## 5. Open a merge request

```bash
cd /tmp/py-demo
git add . && git commit -m "initial"
git remote add origin git@github.com:YOU/py-demo.git
git push -u origin main

pytest -q 2>&1 | tee /tmp/pytest.log

code-agent experts run bug-fix \
  --log /tmp/pytest.log \
  --verify-cmd "pytest -q" \
  -w /tmp/py-demo \
  --publish \
  --base-branch main
```

| Flag | Meaning |
|------|---------|
| `--publish` | Commit fix, push branch, open **draft PR** via `gh` |
| `--base-branch` | PR merges into `main` |

---

## Common mistakes

| Mistake | Fix |
|---------|-----|
| Forgot `-w` | Agent edits wrong directory |
| Wrong `--verify-cmd` | Use exact CI command: `pytest -q` not `python -m pytest` if CI uses `pytest -q` |
| No venv activated | `code-agent: command not found` |
| No `GEMINI_API_KEY` | `doctor` fails — set key first |

[← Back to Quick Start](../quick-start.md)

### Go — failing unit tests {#go-example}

## What do you want?

| Goal | Command |
|------|---------|
| **Fix a broken Go build / failing tests** | `code-agent experts run bug-fix --log /tmp/go.log --verify-cmd "go test ./..." -w .` |
| **Increase coverage** | `code-agent run "increase unit test coverage" --verify-cmd "go test ./..." -w .` |
| **PR line review** | `code-agent experts run code-review --pr N -w .` |

Go projects use **`go test`**, not `pytest`. Always set `--verify-cmd "go test ..."`.

Home quick start (binary first): [Get started](../get-started.md) · [Use cases](../use-cases.md)

---

## 1. Create a failing test

```bash
mkdir -p /tmp/go-demo && cd /tmp/go-demo
git init
go mod init example.com/demo

cat > main.go <<'EOF'
package main

func Add(a, b int) int {
	return a - b // BUG: should be +
}
EOF

cat > main_test.go <<'EOF'
package main

import "testing"

func TestAdd(t *testing.T) {
	if got := Add(2, 3); got != 5 {
		t.Errorf("Add(2,3) = %d; want 5", got)
	}
}
EOF

go test -v ./...
```

**Expected (failure):**

```text
--- FAIL: TestAdd (0.00s)
    main_test.go:6: Add(2,3) = -1; want 5
FAIL
```

**Save log:**

```bash
go test -v ./... 2>&1 | tee /tmp/go-test.log
```

---

## 2. Fix with `code-agent run`

```bash
source /path/to/ai-code-agent/.venv/bin/activate

code-agent run \
  "Fix failing TestAdd in main_test.go. The Add function in main.go has a bug. Run 'go test -v ./...' until all tests pass. Minimal change only." \
  --verify-cmd "go test -v ./..." \
  -w /tmp/go-demo
```

### Flags explained

| Flag | Why for Go |
|------|------------|
| `--verify-cmd "go test -v ./..."` | **Must** be Go's test runner — never `pytest` |
| `-w /tmp/go-demo` | Module root (where `go.mod` lives) |

**Expected:**

```text
Status: done
Files: main.go
```

```bash
cd /tmp/go-demo && go test -v ./...
# PASS
```

---

## 3. Fix with `bug-fix` expert (from log)

```bash
cd /tmp/go-demo
go test -v ./... 2>&1 | tee /tmp/go-test.log

code-agent experts run bug-fix \
  --log /tmp/go-test.log \
  --verify-cmd "go test -v ./..." \
  -w /tmp/go-demo
```

### Flags explained

| Flag | Meaning |
|------|---------|
| `--log /tmp/go-test.log` | Go compiler/test errors parsed automatically |
| `--verify-cmd` | Same command CI uses |
| `-w` | Go module root |
| `--dry-run` | Test locally first, no MR |
| `--publish` | Push fix branch + draft PR |

**Go parser catches:** `main.go:line: undefined`, test failures, build errors.

---

## 4. Fix tests in another repo (real world)

`code-agent` install lives in one folder; **your Go app** in another:

```bash
# Terminal 1 — your Go project
cd ~/karm/my-go-service
go test -v ./... 2>&1 | tee /tmp/go-ci.log

# Terminal 2 — run agent
source ~/karm/ai-code-agent/.venv/bin/activate

code-agent experts run bug-fix \
  --log /tmp/go-ci.log \
  --verify-cmd "go test -v ./..." \
  -w ~/karm/my-go-service
```

!!! warning
    **One** `-w` pointing at the Go repo. Do not point `-w` at `ai-code-agent`.

---

## 5. CI babysit (PR keeps failing)

```bash
code-agent experts watch \
  --pr 42 \
  --verify-cmd "go test -v ./..." \
  -w ~/karm/my-go-service
```

| Flag | Meaning |
|------|---------|
| `--pr 42` | Watch GitHub PR #42 checks |
| `--verify-cmd` | Re-run after each fix attempt |
| `--publish` / `--no-publish` | Push fixes to PR branch (default: publish on) |

---

## Common mistakes

| Mistake | Result |
|---------|--------|
| `--verify-cmd "pytest -q"` on Go repo | Agent runs wrong tool — fails |
| `-w` not at `go.mod` root | Cannot find package |
| Running `go test` outside module | "go.mod not found" |

[← Back to Quick Start](../quick-start.md)

### Java — failing unit tests {#java-example}

## What do you want?

| Goal | Command |
|------|---------|
| **Fix a broken Maven/Gradle build** | `code-agent experts run bug-fix --log /tmp/mvn.log --verify-cmd "mvn test -q" -w .` |
| **Increase coverage** | `code-agent run "add unit tests to raise coverage" --verify-cmd "mvn test -q" -w .` |
| **PR line review** | `code-agent experts run code-review --pr N -w .` |

Java uses **JUnit** + **Maven** or **Gradle**. Set `--verify-cmd` to match your build tool.

Home quick start (binary first): [Get started](../get-started.md) · [Use cases](../use-cases.md)

!!! info "Parser note"
    Dedicated Java/JUnit log parser is limited — `bug-fix` uses **generic error parsing** plus the agent reading test output. **`--verify-cmd` is critical** so the agent proves `mvn test` or `./gradlew test` passes.

---

## Option A — Maven project

### 1. Create a failing test

```bash
mkdir -p /tmp/java-demo && cd /tmp/java-demo
git init

mvn archetype:generate -DgroupId=com.example -DartifactId=demo \
  -DarchetypeArtifactId=maven-archetype-quickstart -DinteractiveMode=false

cd demo

# Introduce bug in main code
cat > src/main/java/com/example/App.java <<'EOF'
package com.example;

public class App {
    public static int add(int a, int b) {
        return a - b; // BUG: should be +
    }
}
EOF

cat > src/test/java/com/example/AppTest.java <<'EOF'
package com.example;

import org.junit.Test;
import static org.junit.Assert.*;

public class AppTest {
    @Test
    public void testAdd() {
        assertEquals(5, App.add(2, 3));
    }
}
EOF

mvn test
```

**Expected:** `BUILD FAILURE` with assertion error in output.

**Save log:**

```bash
mvn test 2>&1 | tee /tmp/java-maven.log
```

### 2. Fix with code-agent

```bash
source /path/to/ai-code-agent/.venv/bin/activate

code-agent run \
  "Fix failing AppTest. The add method in App.java returns wrong result. Run 'mvn test' until BUILD SUCCESS. Change only what is needed." \
  --verify-cmd "mvn test -q" \
  -w /tmp/java-demo/demo
```

### 3. Fix with bug-fix expert

```bash
code-agent experts run bug-fix \
  --log /tmp/java-maven.log \
  --verify-cmd "mvn test -q" \
  -w /tmp/java-demo/demo
```

### Flags explained

| Flag | Value | Why |
|------|-------|-----|
| `-w` | Maven module root (`pom.xml` here) | Agent edits `src/main` and `src/test` |
| `--verify-cmd` | `mvn test -q` | Must match CI — quiet Maven like Actions |
| `--log` | Maven surefire output | Failure class + line from log |

---

## Option B — Gradle project

### 1. Create project + failing test

```bash
mkdir -p /tmp/gradle-demo && cd /tmp/gradle-demo
git init

gradle init --type java-application --dsl kotlin --test-framework junit-jupiter --package com.example --project-name demo
cd demo

# Edit generated code to fail (similar App class + test)
./gradlew test
```

**Save log:**

```bash
./gradlew test 2>&1 | tee /tmp/java-gradle.log
```

### 2. Fix with code-agent

```bash
code-agent experts run bug-fix \
  --log /tmp/java-gradle.log \
  --verify-cmd "./gradlew test" \
  -w /tmp/gradle-demo/demo
```

| Flag | Why |
|------|-----|
| `--verify-cmd "./gradlew test"` | Gradle wrapper — same as CI |
| `-w` | Directory with `build.gradle.kts` |

---

## Add missing unit tests (coverage)

For Java coverage (JaCoCo), use verify command that includes coverage gate:

```bash
# Example — adjust to your pom.xml / build.gradle
mvn test jacoco:report 2>&1 | tee /tmp/java-cov.log

code-agent experts run bug-fix \
  --log /tmp/java-cov.log \
  --verify-cmd "mvn test jacoco:report" \
  -w /path/to/java-project
```

Agent adds tests under `src/test/java/` for uncovered methods.

---

## Open merge request

```bash
code-agent experts run bug-fix \
  --log /tmp/java-maven.log \
  --verify-cmd "mvn test -q" \
  -w /path/to/java-project \
  --publish \
  --base-branch main
```

| Flag | Meaning |
|------|---------|
| `--publish` | Creates branch + draft PR with fix |
| `--base-branch` | Target branch for MR |

Requires `gh auth login`.

---

## Common mistakes

| Mistake | Fix |
|---------|-----|
| `-w` at wrong level | Must be folder with `pom.xml` or `build.gradle` |
| `mvn test` vs `mvn verify` | Use **exact** CI command in `--verify-cmd` |
| JDK not installed | Install JDK 17+; `java -version` must work |
| Mixing Maven and Gradle flags | Pick one build tool per project |

[← Back to Quick Start](../quick-start.md)

---

## Developer & DevOps pains catalog {#pains-catalog}

!!! info "Also on merged page"
    Full content below is preserved. Same section: [use-cases.md#pains-catalog](use-cases.md#pains-catalog).


**Symptom → solution.**

Symptom: your PR is red, the CI log is thousands of lines, coverage gates stall merges, and review still sits on humans—while chat AI claims “fixed” with no proof. You lose nights to archaeology instead of shipping. Solution: **Kramlipi AI Code Agent**. It reads your git repo and the failure signal, edits with real tools, and only stops when **your** verify command exits `0`. Coverage, bug-fix, and PR line review become measured outcomes—not guesses.

Below: every pain we target, what **fixed** looks like, and which command to try. Every fix path is **verify-gated**.

For narrative walkthroughs see [Use Cases](use-cases.md). For flags see [Commands](commands.md).

---

## Developer pains

### Unreadable CI log at 11pm

**Pain:** Thousands of log lines; Slack archaeology; nobody knows if it’s a flake or your PR.  
**Fixed when:** Failure is parsed → scoped fix → **same** verify command exits `0` → optional draft PR with RCA.

```bash
gh run view <RUN_ID> --log-failed > ci.log
code-agent experts run bug-fix \
  --log ci.log --verify-cmd "pytest -q" -w . --publish
```

---

### Passes locally, fails in CI

**Pain:** Green laptop, red pipeline (env, versions, missing services).  
**Fixed when:** You run the agent with the **exact** CI verify command (often in the official container).

```bash
docker run --rm -it -e GEMINI_API_KEY -v "$PWD:/workspace" \
  ghcr.io/kramlipi/code-agent:latest \
  experts run bug-fix --log /workspace/ci.log \
  --verify-cmd "pytest -q" -w /workspace
```

---

### Full suite on every tiny PR

**Pain:** One-file change waits 40+ minutes; CI cost and merge queue pain.  
**Fixed when:** Diff → impacted tests → selective verify command (fallback to full suite when unsure).

```bash
code-agent experts run test-intel --base-branch main -w .
```

---

### Coverage gate blocks merge

**Pain:** “80% not reached”; temptation to weaken the gate.  
**Fixed when:** Agent **adds tests**; coverage command still exits `0`.

```bash
code-agent run \
  "Add unit tests for src/pkg/new_feature.py. Match tests/ style." \
  --verify-cmd "pytest -q --cov=pkg --cov-fail-under=80" -w .
```

---

### No first-pass PR review on every change

**Pain:** PRs merge with obvious bugs, secrets, or broken APIs; senior review doesn’t scale.  
**Fixed when:** Automated **inline comments** on the PR diff (comment-only); humans still own design sign-off.

```bash
code-agent experts run code-review --pr 42 -w .
code-agent experts run code-review --pr 42 --dry-run -w .
```

---

### Same PR fails again and again

**Pain:** Fix → push → new failure → all-day context switch.  
**Fixed when:** Watcher polls checks and re-runs the fix loop until green or max attempts.

```bash
code-agent experts watch --pr 42 --verify-cmd "pytest -q" -w .
```

---

### Flaky tests burn trust

**Pain:** Random red; people re-run until green; real bugs hide.  
**Fixed when:** Known flaky tests can be skipped in selective plans **with a report**; current failures still get fixed.  
**Honest limit:** Strong statistical flake scoring is not shipped yet — use `bug-fix` on the **current** failure and human quarantine for chronic flakes.

---

### Lint / type / format debt after a rule change

**Pain:** New mypy/ruff/eslint rule; hundreds of files; merge blocked on style.  
**Fixed when:** Narrow verify is green; edits stay scoped.

```bash
code-agent run "Fix mypy errors in src/utils.py only." \
  --verify-cmd "mypy src/utils.py" -w .
```

---

### Unfamiliar repo — where do I start?

**Pain:** New hire / rotation; failing tests; fear of breaking main.  
**Fixed when:** Doctor shows which verify would run; chat/UI can explore; dry-run before writes.

```bash
code-agent doctor --verify-plan "fix failing unit tests" -w .
code-agent chat -w .
```

---

### Dependency / Dependabot PR is red

**Pain:** Version bump breaks callers; bot PR sits red for weeks.  
**Fixed when:** Failed upgrade CI log → app/adapter fix → verify green → human merge.

```bash
code-agent experts run bug-fix \
  --log /tmp/dependabot-ci.log \
  --verify-cmd "pytest -q" -w .
```

---

### AI claimed “fixed” without proof

**Pain:** Chatbots invent success; trust collapses.  
**Fixed when:** Agent cannot finish successfully unless your verify subprocess exits `0`.

```bash
code-agent run "Fix failing unit tests" --verify-cmd "pytest -q" -w .
```

---

### Refactor left broken imports

**Pain:** Rename/package move; tests and callers lag.  
**Fixed when:** Language verify (`pytest`, `go test`, `mvn test`, …) exits `0`.

See [Python](examples/python.md) · [Go](examples/go.md) · [Java](examples/java.md).

---

## DevOps / platform / SRE pains

### Platform is the eternal CI babysitter

**Pain:** Every team pings platform to read logs.  
**Fixed when:** One golden-path command works on every service (same exit codes).

```bash
code-agent experts run bug-fix --log ci.log --verify-cmd "pytest -q" -w "$REPO"
```

---

### CI minutes / runner cost explode

**Pain:** Full suites on every push; finance asks why the bill doubled.  
**Fixed when:** Selective tests on PRs via `test-intel`; org workflow template.

```bash
code-agent experts run test-intel --base-branch main -w .
```

---

### Flapping pipelines → duplicate bot PRs

**Pain:** Overnight spam of identical “fix” MRs.  
**Fixed when:** Dedup by failure fingerprint (same failure within TTL → skip).

Built into `bug-fix` — no extra flags.

---

### Agents must not cheat CI

**Pain:** Fear that AI will edit workflows or disable checks to go green.  
**Fixed when:** Forbidden paths (e.g. `.github/workflows`) enforced; review the draft MR.

---

### Missing metrics / SLO before release

**Pain:** Readiness asks for latency/error metrics; manual grep does not scale.  
**Fixed when:** Scan → gap report; optional draft MR with instrumentation.

```bash
code-agent experts run monitoring-expert -w . --dry-run
code-agent experts run monitoring-expert -w . --publish
```

---

### Alert fired — kubectl roulette

**Pain:** PagerDuty noise; tribal knowledge; manual prod edits.  
**Fixed when:** Alert → code/config remediations → health verify → draft MR (start with `--dry-run`).

```bash
code-agent experts run sre-expert \
  --log ./alert.json \
  --verify-cmd "curl -sf http://localhost:8080/health" \
  -w . --dry-run
```

---

### Post-deploy — is the canary safe?

**Pain:** Metrics tick up; nobody owns go/no-go.  
**Fixed when:** Compare to baseline → `pass` / `block` / `rollback` artifact.

```bash
code-agent experts run deploy-guard --metrics-file metrics/current.json -w .
```

---

### Webhooks should trigger experts (no SSH)

**Pain:** Events need HTTP intake; jump hosts do not scale.  
**Fixed when:** `experts serve` behind auth with budget/throttle gates.

```bash
code-agent experts serve --host 0.0.0.0 --port 8787 -w /path/to/checkout
```

---

### Locked-down laptops (no local pip)

**Pain:** Security blocks local Python installs.  
**Fixed when:** Official image + mounted workspace.

```bash
docker pull ghcr.io/kramlipi/code-agent:latest
# see Quick Start for docker-ui.sh
```

---

### Nightly job red for days

**Pain:** Scheduled pipeline fails unnoticed until Monday.  
**Fixed when:** On `failure()`, run `bug-fix` → draft MR + notify (wire in Actions/GitLab).

---

### Compliance — what did the bot change?

**Pain:** SOC2 / customer asks for an audit trail.  
**Fixed when:** Every run leaves artifacts under `.code-agent/runs/` (signals, verify, diff).

---

## What we are not (yet)

| Pain | Reality |
|------|---------|
| “Review every PR like a senior” | We babysit **CI green**, not design review |
| “Auto-mark flaky and forget” | No strong flake scorer yet — fix current failure; quarantine by policy |
| “Edit workflows to make green” | **Blocked** by safety |
| “Fix Terraform/Helm as a first-class expert” | Use custom `--verify-cmd` today; dedicated IaC path is later |
| “Replace staging / kubectl” | Agent edits **code**; pair with `deploy-guard` for metrics gates |

---

## Quick picker

| I need to… | Start here |
|------------|------------|
| Fix CI from a log | `experts run bug-fix --log …` |
| Run fewer tests on a PR | `experts run test-intel` |
| Raise coverage | `run` / `bug-fix` + cov verify |
| Babysit a flapping PR | `experts watch --pr N` |
| Find missing metrics | `experts run monitoring-expert` |
| Alert → code fix | `experts run sre-expert` |
| Post-deploy metrics gate | `experts run deploy-guard` |
| Prove “done” | always `--verify-cmd` |
| No local Python | Docker / [Quick Start](quick-start.md) |

---

## Related

- [Early adopter use cases](use-cases.md) — why / command / benefit in depth  
- [Recipes](recipes.md) — copy-paste only  
- [Experts](experts.md) — inputs and outputs  
- [Commands](commands.md) — CLI reference including verify how-to  

---

## Language walkthroughs {#language-walkthroughs}

### Python — failing unit tests {#python-example}

!!! info "Also on merged page"
    Full content below is preserved. Same section: [use-cases.md#python-example](use-cases.md#python-example).


## What do you want?

| Goal | Command |
|------|---------|
| **Fix a broken build / failing pytest** | `code-agent experts run bug-fix --log /tmp/ci.log --verify-cmd "pytest -q" -w .` |
| **Increase coverage** | `code-agent run "increase unit test coverage" --verify-cmd "pytest -q --cov=PKG --cov-fail-under=80" -w .` |
| **PR line review** | `code-agent experts run code-review --pr N -w .` |

End-to-end below: **create a failing test → fix with code-agent**.

**Full narrative tutorial:** [Fix Failing Python Tests Until pytest Is Green](../articles/tutorial-python-failing-tests.md)

Home quick start (binary first): [Get started](../get-started.md) · [Use cases](../use-cases.md) · [All tutorials](../articles/index.md)

---

## 1. Create a failing test (in your repo)

```bash
mkdir -p /tmp/py-demo && cd /tmp/py-demo
git init

# Minimal package
mkdir -p myapp tests
cat > myapp/__init__.py <<'EOF'
def add(a: int, b: int) -> int:
    return a + b
EOF

cat > myapp/calc.py <<'EOF'
def add(a: int, b: int) -> int:
    return a - b   # BUG: should be +
EOF

cat > tests/test_calc.py <<'EOF'
from myapp.calc import add

def test_add():
    assert add(2, 3) == 5
EOF

pip install pytest
pytest -q
```

**Expected (failure):**

```text
FAILED tests/test_calc.py::test_add - assert -1 == 5
1 failed
```

**Save the log:**

```bash
pytest -q 2>&1 | tee /tmp/pytest.log
```

---

## 2. Fix with `code-agent run` (prompt mode)

```bash
source /path/to/ai-code-agent/.venv/bin/activate

code-agent run \
  "Fix the failing test in tests/test_calc.py. The add() function in myapp/calc.py is wrong. Run pytest -q until all tests pass. Change only what is needed." \
  --verify-cmd "pytest -q" \
  -w /tmp/py-demo
```

### Flags explained

| Flag | Value | Meaning |
|------|-------|---------|
| `"..."` | task text | What you want — plain English |
| `--verify-cmd` | `pytest -q` | Agent must run this and get exit `0` before finishing |
| `-w` | `/tmp/py-demo` | **Workspace** — only this repo is edited |

**Expected:**

```text
Status: done
Files: myapp/calc.py
```

**Verify yourself:**

```bash
cd /tmp/py-demo && pytest -q
# 1 passed
```

---

## 3. Fix with `bug-fix` expert (CI log mode)

Best when CI already failed and you have a log file.

```bash
cd /tmp/py-demo
pytest -q 2>&1 | tee /tmp/pytest.log

code-agent experts run bug-fix \
  --log /tmp/pytest.log \
  --verify-cmd "pytest -q" \
  -w /tmp/py-demo
```

### Flags explained

| Flag | Meaning | Why use it |
|------|---------|------------|
| `--log` | Path to pytest output | Expert **parses** failures (file, line, assertion) — no guessing |
| `--verify-cmd` | Must match what CI runs | Same proof as GitHub Actions |
| `-w` | Your Python repo | Agent edits `myapp/` and `tests/` here |
| `--dry-run` | (optional) Try without publish | First safe run |
| `--publish` | (optional) Open draft PR | After local verify works |

**Parser support:** pytest failures, coverage failures, Python tracebacks, mypy.

---

## 4. Raise coverage (add missing unit tests)

Break coverage on purpose:

```bash
cat >> myapp/calc.py <<'EOF'

def multiply(a: int, b: int) -> int:
    return a * b
EOF

# No test for multiply yet
pytest -q --cov=myapp --cov-report=term-missing --cov-fail-under=80 2>&1 | tee /tmp/cov.log
```

Fix:

```bash
code-agent experts run bug-fix \
  --log /tmp/cov.log \
  --verify-cmd "pytest -q --cov=myapp --cov-report=term-missing --cov-fail-under=80" \
  -w /tmp/py-demo
```

Agent adds tests in `tests/` — does **not** remove `multiply()` to cheat.

---

## 5. Open a merge request

```bash
cd /tmp/py-demo
git add . && git commit -m "initial"
git remote add origin git@github.com:YOU/py-demo.git
git push -u origin main

pytest -q 2>&1 | tee /tmp/pytest.log

code-agent experts run bug-fix \
  --log /tmp/pytest.log \
  --verify-cmd "pytest -q" \
  -w /tmp/py-demo \
  --publish \
  --base-branch main
```

| Flag | Meaning |
|------|---------|
| `--publish` | Commit fix, push branch, open **draft PR** via `gh` |
| `--base-branch` | PR merges into `main` |

---

## Common mistakes

| Mistake | Fix |
|---------|-----|
| Forgot `-w` | Agent edits wrong directory |
| Wrong `--verify-cmd` | Use exact CI command: `pytest -q` not `python -m pytest` if CI uses `pytest -q` |
| No venv activated | `code-agent: command not found` |
| No `GEMINI_API_KEY` | `doctor` fails — set key first |

[← Back to Quick Start](../quick-start.md)

### Go — failing unit tests {#go-example}

!!! info "Also on merged page"
    Full content below is preserved. Same section: [use-cases.md#go-example](use-cases.md#go-example).


## What do you want?

| Goal | Command |
|------|---------|
| **Fix a broken Go build / failing tests** | `code-agent experts run bug-fix --log /tmp/go.log --verify-cmd "go test ./..." -w .` |
| **Increase coverage** | `code-agent run "increase unit test coverage" --verify-cmd "go test ./..." -w .` |
| **PR line review** | `code-agent experts run code-review --pr N -w .` |

Go projects use **`go test`**, not `pytest`. Always set `--verify-cmd "go test ..."`.

**Full narrative tutorial:** [Fix Failing Go Tests Until `go test` Is Green](../articles/tutorial-go-failing-tests.md)

Home quick start (binary first): [Get started](../get-started.md) · [Use cases](../use-cases.md) · [All tutorials](../articles/index.md)

---

## 1. Create a failing test

```bash
mkdir -p /tmp/go-demo && cd /tmp/go-demo
git init
go mod init example.com/demo

cat > main.go <<'EOF'
package main

func Add(a, b int) int {
	return a - b // BUG: should be +
}
EOF

cat > main_test.go <<'EOF'
package main

import "testing"

func TestAdd(t *testing.T) {
	if got := Add(2, 3); got != 5 {
		t.Errorf("Add(2,3) = %d; want 5", got)
	}
}
EOF

go test -v ./...
```

**Expected (failure):**

```text
--- FAIL: TestAdd (0.00s)
    main_test.go:6: Add(2,3) = -1; want 5
FAIL
```

**Save log:**

```bash
go test -v ./... 2>&1 | tee /tmp/go-test.log
```

---

## 2. Fix with `code-agent run`

```bash
source /path/to/ai-code-agent/.venv/bin/activate

code-agent run \
  "Fix failing TestAdd in main_test.go. The Add function in main.go has a bug. Run 'go test -v ./...' until all tests pass. Minimal change only." \
  --verify-cmd "go test -v ./..." \
  -w /tmp/go-demo
```

### Flags explained

| Flag | Why for Go |
|------|------------|
| `--verify-cmd "go test -v ./..."` | **Must** be Go's test runner — never `pytest` |
| `-w /tmp/go-demo` | Module root (where `go.mod` lives) |

**Expected:**

```text
Status: done
Files: main.go
```

```bash
cd /tmp/go-demo && go test -v ./...
# PASS
```

---

## 3. Fix with `bug-fix` expert (from log)

```bash
cd /tmp/go-demo
go test -v ./... 2>&1 | tee /tmp/go-test.log

code-agent experts run bug-fix \
  --log /tmp/go-test.log \
  --verify-cmd "go test -v ./..." \
  -w /tmp/go-demo
```

### Flags explained

| Flag | Meaning |
|------|---------|
| `--log /tmp/go-test.log` | Go compiler/test errors parsed automatically |
| `--verify-cmd` | Same command CI uses |
| `-w` | Go module root |
| `--dry-run` | Test locally first, no MR |
| `--publish` | Push fix branch + draft PR |

**Go parser catches:** `main.go:line: undefined`, test failures, build errors.

---

## 4. Fix tests in another repo (real world)

`code-agent` install lives in one folder; **your Go app** in another:

```bash
# Terminal 1 — your Go project
cd ~/karm/my-go-service
go test -v ./... 2>&1 | tee /tmp/go-ci.log

# Terminal 2 — run agent
source ~/karm/ai-code-agent/.venv/bin/activate

code-agent experts run bug-fix \
  --log /tmp/go-ci.log \
  --verify-cmd "go test -v ./..." \
  -w ~/karm/my-go-service
```

!!! warning
    **One** `-w` pointing at the Go repo. Do not point `-w` at `ai-code-agent`.

---

## 5. CI babysit (PR keeps failing)

```bash
code-agent experts watch \
  --pr 42 \
  --verify-cmd "go test -v ./..." \
  -w ~/karm/my-go-service
```

| Flag | Meaning |
|------|---------|
| `--pr 42` | Watch GitHub PR #42 checks |
| `--verify-cmd` | Re-run after each fix attempt |
| `--publish` / `--no-publish` | Push fixes to PR branch (default: publish on) |

---

## Common mistakes

| Mistake | Result |
|---------|--------|
| `--verify-cmd "pytest -q"` on Go repo | Agent runs wrong tool — fails |
| `-w` not at `go.mod` root | Cannot find package |
| Running `go test` outside module | "go.mod not found" |

[← Back to Quick Start](../quick-start.md)

### Java — failing unit tests {#java-example}

!!! info "Also on merged page"
    Full content below is preserved. Same section: [use-cases.md#java-example](use-cases.md#java-example).


## What do you want?

| Goal | Command |
|------|---------|
| **Fix a broken Maven/Gradle build** | `code-agent experts run bug-fix --log /tmp/mvn.log --verify-cmd "mvn test -q" -w .` |
| **Increase coverage** | `code-agent run "add unit tests to raise coverage" --verify-cmd "mvn test -q" -w .` |
| **PR line review** | `code-agent experts run code-review --pr N -w .` |

Java uses **JUnit** + **Maven** or **Gradle**. Set `--verify-cmd` to match your build tool.

**Full narrative tutorial:** [Fix Failing Java Tests Until Maven/Gradle Is Green](../articles/tutorial-java-failing-tests.md)

Home quick start (binary first): [Get started](../get-started.md) · [Use cases](../use-cases.md) · [All tutorials](../articles/index.md)

!!! info "Parser note"
    Dedicated Java/JUnit log parser is limited — `bug-fix` uses **generic error parsing** plus the agent reading test output. **`--verify-cmd` is critical** so the agent proves `mvn test` or `./gradlew test` passes.

---

## Option A — Maven project

### 1. Create a failing test

```bash
mkdir -p /tmp/java-demo && cd /tmp/java-demo
git init

mvn archetype:generate -DgroupId=com.example -DartifactId=demo \
  -DarchetypeArtifactId=maven-archetype-quickstart -DinteractiveMode=false

cd demo

# Introduce bug in main code
cat > src/main/java/com/example/App.java <<'EOF'
package com.example;

public class App {
    public static int add(int a, int b) {
        return a - b; // BUG: should be +
    }
}
EOF

cat > src/test/java/com/example/AppTest.java <<'EOF'
package com.example;

import org.junit.Test;
import static org.junit.Assert.*;

public class AppTest {
    @Test
    public void testAdd() {
        assertEquals(5, App.add(2, 3));
    }
}
EOF

mvn test
```

**Expected:** `BUILD FAILURE` with assertion error in output.

**Save log:**

```bash
mvn test 2>&1 | tee /tmp/java-maven.log
```

### 2. Fix with code-agent

```bash
source /path/to/ai-code-agent/.venv/bin/activate

code-agent run \
  "Fix failing AppTest. The add method in App.java returns wrong result. Run 'mvn test' until BUILD SUCCESS. Change only what is needed." \
  --verify-cmd "mvn test -q" \
  -w /tmp/java-demo/demo
```

### 3. Fix with bug-fix expert

```bash
code-agent experts run bug-fix \
  --log /tmp/java-maven.log \
  --verify-cmd "mvn test -q" \
  -w /tmp/java-demo/demo
```

### Flags explained

| Flag | Value | Why |
|------|-------|-----|
| `-w` | Maven module root (`pom.xml` here) | Agent edits `src/main` and `src/test` |
| `--verify-cmd` | `mvn test -q` | Must match CI — quiet Maven like Actions |
| `--log` | Maven surefire output | Failure class + line from log |

---

## Option B — Gradle project

### 1. Create project + failing test

```bash
mkdir -p /tmp/gradle-demo && cd /tmp/gradle-demo
git init

gradle init --type java-application --dsl kotlin --test-framework junit-jupiter --package com.example --project-name demo
cd demo

# Edit generated code to fail (similar App class + test)
./gradlew test
```

**Save log:**

```bash
./gradlew test 2>&1 | tee /tmp/java-gradle.log
```

### 2. Fix with code-agent

```bash
code-agent experts run bug-fix \
  --log /tmp/java-gradle.log \
  --verify-cmd "./gradlew test" \
  -w /tmp/gradle-demo/demo
```

| Flag | Why |
|------|-----|
| `--verify-cmd "./gradlew test"` | Gradle wrapper — same as CI |
| `-w` | Directory with `build.gradle.kts` |

---

## Add missing unit tests (coverage)

For Java coverage (JaCoCo), use verify command that includes coverage gate:

```bash
# Example — adjust to your pom.xml / build.gradle
mvn test jacoco:report 2>&1 | tee /tmp/java-cov.log

code-agent experts run bug-fix \
  --log /tmp/java-cov.log \
  --verify-cmd "mvn test jacoco:report" \
  -w /path/to/java-project
```

Agent adds tests under `src/test/java/` for uncovered methods.

---

## Open merge request

```bash
code-agent experts run bug-fix \
  --log /tmp/java-maven.log \
  --verify-cmd "mvn test -q" \
  -w /path/to/java-project \
  --publish \
  --base-branch main
```

| Flag | Meaning |
|------|---------|
| `--publish` | Creates branch + draft PR with fix |
| `--base-branch` | Target branch for MR |

Requires `gh auth login`.

---

## Common mistakes

| Mistake | Fix |
|---------|-----|
| `-w` at wrong level | Must be folder with `pom.xml` or `build.gradle` |
| `mvn test` vs `mvn verify` | Use **exact** CI command in `--verify-cmd` |
| JDK not installed | Install JDK 17+; `java -version` must work |
| Mixing Maven and Gradle flags | Pick one build tool per project |

[← Back to Quick Start](../quick-start.md)