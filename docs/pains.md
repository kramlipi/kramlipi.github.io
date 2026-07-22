---
title: Developer & DevOps pains
description: >-
  Catalog of developer and DevOps pains code-agent targets — what hurts, what
  “fixed” means, and which command to run for each use case.
keywords: developer pain, devops pain, ci failure, flaky tests, coverage, sre, use cases
---

!!! info "Also on merged page"
    Full content below is preserved. Same section: [use-cases.md#pains-catalog](use-cases.md#pains-catalog).

# Developer & DevOps pains

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
