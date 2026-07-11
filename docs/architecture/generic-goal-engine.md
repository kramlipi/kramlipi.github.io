---
title: Design — Generic Goal Engine (summary)
description: >-
  Discover SuccessSpec → act with tools → objective gate. Fail-closed,
  jailed, no unrestricted shell. Phase A–D roadmap.
keywords: architecture, SuccessSpec, run_command, Observation, code-agent design
---

# Design summary: Generic Goal-Seeking Engine

Authoritative long-form design lives in the code-agent repo:  
`docs/DESIGN-generic-goal-engine.md` (branch `design/generic-goal-engine`).

## Problem

Claude Code / Cursor can discover `npm test` / `pytest`, run it, read logs, edit, and re-run.  
code-agent historically injected `--verify-cmd` from outside the model and had **no** mid-loop shell tool.

## Stance (locked)

| Do | Don’t |
|----|--------|
| Discover SuccessSpec from manifests / CI / flags | Unrestricted `bash -c` |
| Edit **source** until the chosen script is green | Edit `.github/workflows/**` to force green |
| Subprocess exit code as hard gate | Let the LLM declare success over a red verify |
| Policy-gated `run_command` (Phase B) | Replace CI **parsers** with LLM log reading for intake |

## Control flow

```text
Discover → Planner → Executor (file tools [+ run_command later]) → Verifier (success_cmd)
                ↑                                                      |
                └──────────────── retry on fail ───────────────────────┘
```

## Phases

| Phase | Deliverable |
|-------|-------------|
| **A** | SuccessSpec types + naming; `verify_cmd` remains the gate |
| **B** | Allowlisted `run_command` + Observation buffer |
| **C** | UI: show resolved success cmd / candidates |
| **D** | Optional auto-followup after verify fail |

## Try it

See **[Goal engine — sample commands](goal-engine.md)**.

Contact: cluevion@gmail.com · https://kramlipi.github.io
