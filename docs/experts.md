---
title: Experts
description: >-
  code-agent automation experts — bug-fix, test-intel, deploy-guard, sre-expert,
  and monitoring-expert with inputs, outputs, and example commands.
keywords: bug-fix expert, test-intel, deploy-guard, sre-expert, monitoring-expert
---

# Experts

Experts wrap the agent loop with **intake → triage → fix → verify → publish**.

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
