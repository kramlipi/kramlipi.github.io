---
title: Flaky test admin
description: >-
  Remember flaky tests, choose SQLite or Postgres storage, see evidence in the
  console, and skip on merge requests — customer-hosted test intelligence.
keywords: >-
  flaky tests, test intelligence, postgres memory, skip flaky tests, code-agent
  admin, merge request, CI memory
---

# Flaky tests — remember, review, skip

Your suite already knows which tests lie. Kramlipi **writes that down** — pass and fail history, same-commit evidence, and a place for admins to say “skip this on MR until we fix it.”

**Not CodeRabbit.** Review bots comment on code. They do not keep a shared flake registry or let you pick SQLite vs Postgres for test outcomes. This page is for teams tired of re-discovering the same red test every sprint.

---

## What you get

| Capability | In plain language |
|------------|-------------------|
| **Memory** | Every test run you record adds to history — local file or shared Postgres. |
| **Detection** | Same test pass+fail on one commit, or mixed results over recent runs → flake candidate. |
| **Console** | Web UI right rail: flaky builds, ranked tests, notifications. |
| **Skip on MR** | `test-intel` runs diff-scoped tests and skips known flakes — reasons in the report. |
| **Admin overrides** | Force skip or force run; no silent `@skip` in source unless you choose quarantine. |

All of it runs **on your machine or CI**, with **your** database URL and **your** API keys.

---

## Start in five minutes (SQLite)

No extra packages. Memory lives in `.code-agent/memory.sqlite` inside the repo workspace.

### Record outcomes from a PR

```bash
code-agent experts run test-intel --pr 42 --run-tests \
  -w /path/to/repo \
  --verify-cmd "pytest -q"
```

### Check memory from the terminal

```bash
code-agent memory status
code-agent memory flakes
```

### Use the visual console

```bash
export GEMINI_API_KEY=your-key
code-agent web serve
```

1. Open **http://127.0.0.1:8080**
2. Look at the right rail — **Flaky build intelligence**
3. Click **↻** to sync recent GitHub Actions runs (needs `gh` auth)
4. Click **Skip on MR** on a test, or **⚙** for storage settings

!!! note "Who can change settings?"
    Admin save and overrides work from **localhost** by default.  
    In Docker on a private network: `CODE_AGENT_ALLOW_UI_ADMIN=1`.

---

## Admin — where test results are stored

Open **⚙** (gear) on the flake panel.

=== "SQLite (default)"

    Best for one repo, one machine, or CI with a cached file.

    - **Path:** `.code-agent/memory.sqlite` (under workspace)
    - **Save** writes `config.yaml` in the repo workspace
    - **Tip:** Cache `.code-agent/` in GitHub Actions between runs

=== "Postgres (team / org)"

    Best when many runners or repos should share one history.

    ```bash
    pip install 'code-agent[memory]'
    ```

    Set URL in the admin sheet **or** environment:

    ```bash
    export CODE_AGENT_MEMORY_POSTGRES_URL='postgres://user:pass@host:5432/code_agent'
    ```

    In `config.yaml`:

    ```yaml
    experts:
      memory:
        backend: postgres
        postgres_url: postgres://...
        skip_flaky_on_mr: true
    ```

Toggle **Skip known flaky tests on MR runs** to turn automatic skip on or off without losing history.

---

## Skip a test when you already know

History is great; judgment is faster.

**In the UI**

- **Skip on MR** on any test row in the flake panel, or  
- Admin sheet → manual overrides list

**With curl** (localhost)

```bash
curl -X POST http://127.0.0.1:8080/api/admin/memory/flakes/override \
  -H 'Content-Type: application/json' \
  -d '{
    "test_node": "tests/test_checkout.py::test_inventory_race",
    "action": "skip",
    "reason": "platform team tracking in JIRA-1234"
  }'
```

| Action | What happens on the next MR |
|--------|----------------------------|
| `skip` | Test is not run; reason appears in `mr_test_report.json` |
| `force_run` | Test runs even if memory says flaky |
| `clear` | Back to automatic detection only |

---

## Wire it into CI

Add to pull-request workflow:

```yaml
- name: Diff-scoped tests + flake memory
  run: |
    code-agent experts run test-intel \
      --pr ${{ github.event.pull_request.number }} \
      --run-tests --emit-ci \
      -w . --verify-cmd "pytest -q"
```

- **SQLite:** cache `.code-agent/memory.sqlite`
- **Postgres:** same `postgres_url` on every job

Read the report:

```bash
code-agent memory status --pr 42
```

---

## How we decide “flaky”

!!! info "Build flake (high confidence)"
    Same GitHub workflow name + **same commit SHA** → at least one pass and one fail.  
    Cancelled or in-progress runs do not count.

!!! info "Test flake (scored candidate)"
    Pass and fail in recent runs, or pass+fail on the same SHA enough times (default: 3 outcomes on that SHA).

!!! warning "Honest limits"
    - Cold start: run tests once or ingest JUnit before memory is useful  
    - Python/pytest path is strongest today  
    - Score is evidence, not oracle — use admin skip when the team already knows  

To **fix** root cause (not just skip), use the `flake` expert or scheduled `flaky-fix` — see [Experts](experts.md).

---

## vs CodeRabbit

| Question | CodeRabbit | Kramlipi |
|----------|------------|----------|
| Stores pass/fail history? | No | SQLite or Postgres |
| Skip flaky tests on MR? | No | Yes, logged |
| Admin picks DB? | — | Yes (web UI) |
| Same-SHA flake proof? | — | Yes |
| Primary job | PR review comments | Verify-gated CI + test intel |

CodeRabbit **fix-ci** tries to patch a failing check in a sandbox. Kramlipi **remembers** which tests oscillate and **skips them on purpose** while you ship — then helps repair or quarantine with the flake expert.

---

## Related pages

- [Get started](get-started.md) — binary, keys, first run  
- [Use cases — run only tests that matter](use-cases.md#2-run-only-the-tests-that-matter)  
- [Quick start](quick-start.md) — Docker UI  
- [Experts](experts.md) — `test-intel`, `flake`  

**Product source:** [runningcodeio/ai-code-agent](https://github.com/runningcodeio/ai-code-agent) · docs synced from `docs/FLAKY-TEST-ADMIN.md`
