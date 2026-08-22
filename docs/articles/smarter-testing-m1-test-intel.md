---
title: Smarter Testing on GitHub Actions — Run Only Tests Your PR Touches
description: >-
  New test-intel M1 — doc-only PRs skip the suite, coverage contexts pick impacted
  tests, same-SHA flake memory skips noise, and JUnit timings feed better shards.
keywords: >-
  smarter testing, test impact analysis, code-agent test-intel, CircleCI Chunk alternative,
  pytest coverage contexts, flaky tests, GitHub Actions CI
---

# Smarter Testing on GitHub Actions — Run Only Tests Your PR Touches

Your PR changes two lines in a README. CI still runs four hundred tests for twelve minutes.

That is not a model problem. It is a **selection** problem — and CircleCI’s Chunk / Smarter Testing solved it by sitting inside their platform with months of stored results.

**Kramlipi code-agent** now ships the portable half of that story: **verify-gated repair** plus **test-intel M1** — impact selection, flake memory, and timing-aware shards — on **GitHub Actions, GitLab, or your laptop**, without migrating to CircleCI.

This post covers what landed, how to turn it on, and what we still do not claim.

---

## What M1 adds (honest summary)

| Capability | What it does |
|------------|--------------|
| **Doc-only diffs** | README / docs-only PR → **zero tests** in the plan |
| **Line-precision impact** | `coverage.py` JSON with `cov-context=test` → run tests that cover changed lines |
| **Import graph fallback** | Python reverse-import map when contexts are missing |
| **Same-SHA flake memory** | Pass **and** fail on the **same commit** across **≥3 runs** → skip on the next MR |
| **JUnit → timings** | `test-intel --run-tests` merges durations into `.code-agent/test-timing.json` for shards |
| **Doctor** | `code-agent doctor --test-intel` checks coverage, contexts, memory, compose verify |
| **Fix deep link** | Failed Actions run → web UI preloads `run_id` / log URL for bug-fix |

We are **not** claiming full CircleCI Chunk parity (no in-UI fix buttons on every job step, no org-wide cross-repo analytics). We **are** claiming a faster, safer loop for teams already on GitHub Actions with a real verify command.

---

## Step 1 — Generate coverage with test contexts

File-level Cobertura is not enough for line-precision. Run pytest once with **contexts**:

```bash
cd /path/to/your-repo

pytest -q \
  --cov=src \
  --cov-report=xml:.code-agent/coverage.xml \
  --cov-context=test
```

That produces `.code-agent/coverage.json` alongside the XML. Commit the `.code-agent/` convention or generate it in CI before `test-intel` runs.

Check setup:

```bash
code-agent doctor --test-intel -w .
```

If you see **“coverage contexts — file-level only”**, add the JSON step above. Under `--test-intel`, missing contexts fail the check.

---

## Step 2 — Plan impacted tests on a PR

Against `main` (or your default branch):

```bash
export CODE_AGENT_MODEL=gemini/gemini-2.0-flash
export GEMINI_API_KEY=your-key-here

code-agent experts run test-intel --base-branch main -w .
```

**Output:** `.code-agent/runs/<run_id>/test_plan.json` with:

- `impacted_tests` — pytest node ids (or scoped files)
- `verify_cmd` — copy-paste command for CI
- `tests_skipped_flaky` — known flakes removed from the run list

Doc-only example: change only `docs/guide.md` → plan method `doc-only`, empty test list, `verify_cmd` may be `true`.

---

## Step 3 — Wire into GitHub Actions (sketch)

Run the plan, then execute only what it selected:

```yaml
- name: Test impact plan
  run: |
    code-agent experts run test-intel --base-branch main > /tmp/plan.txt
    VERIFY=$(jq -r '.verify_cmd' .code-agent/runs/*/test_plan.json | tail -1)
    echo "verify=$VERIFY" >> "$GITHUB_OUTPUT"

- name: Run impacted tests
  run: ${{ steps.plan.outputs.verify }}
```

For **timing-aware shards**, add `--run-tests` locally or in CI so JUnit is merged:

```bash
code-agent experts run test-intel --base-branch main --run-tests -w .
```

Each run appends testcase durations to `.code-agent/test-timing.json` for better parallel splits.

---

## Step 4 — Flake memory (skip noise on the next MR)

After a few CI runs with outcomes recorded (JUnit ingest or `--run-tests`), `test-intel` skips tests that **both passed and failed on the same commit SHA** at least **three times** — not a single unlucky rerun.

Tune in config:

```yaml
# .code-agent/config.yaml (example)
experts:
  memory:
    min_same_sha_runs: 3
    skip_flaky_on_mr: true
```

Inspect:

```bash
code-agent memory flakes -w .
```

Scheduled auto-fix PRs (`experts schedule flaky-fix`) remain **opt-in** — same engine as bug-fix, verify-gated.

---

## Step 5 — One-click fix from a failed Actions run (beta)

When CI fails, a GitHub Check Run can deep-link to the Kramlipi web UI with the run id and log URL pre-filled:

```
https://your-ui-host/?run_id=12345678&log_url=https://github.com/org/repo/actions/runs/12345678&expert=bug-fix
```

Enable the `fix-check-run-template` workflow in your repo and set `CODE_AGENT_WEB_BASE`. The agent still must pass **your** `verify_cmd` — no green, no done.

---

## How this compares to CircleCI Chunk

| | CircleCI Chunk / Smarter Testing | Kramlipi test-intel M1 |
|--|----------------------------------|-------------------------|
| Platform | CircleCI-native buttons + history | Vendor-agnostic CLI / Actions |
| Impact selection | Coverage map + org history | Contexts + import graph + golden proof |
| Trust gate | Agent in CircleCI executor | **Your** `verify_cmd` subprocess |
| Flake lifecycle | Scheduled fix + N validation runs | Same-SHA score + skip-on-MR + optional schedule |
| Honest gap | Deep UI integration | Always-on JUnit ingest habit still on you |

**Bottom line:** If you already trust `pytest -q` (or `go test ./...`) as the scoreboard, test-intel shrinks what runs on each PR while bug-fix keeps owning green CI.

---

## Try it today

1. Download **code-agent** from [GitHub Releases](https://github.com/kramlipi/code-agent-binaries/releases)
2. `code-agent doctor --test-intel -w .`
3. `code-agent experts run test-intel --base-branch main -w .`
4. Read the plan: `.code-agent/runs/*/test_plan.json`

**More tutorials:** [Tutorials & Blog](index.md) · [test-intel in Features](../features.md) · [Use cases](../use-cases.md)

**Contact:** cluevion@gmail.com
