---
title: Troubleshooting
description: >-
  Troubleshoot code-agent exit codes, doctor failures, verify_cmd errors, LLM
  provider issues, and expert skip/fail states.
keywords: code-agent troubleshooting, exit code, doctor failed, verify_cmd
---

# Troubleshooting

## Exit codes

| Code | Meaning | What to do |
|------|---------|------------|
| `0` | Success | — |
| `1` | Startup / config / doctor | Run `code-agent doctor`; check `config.yaml`, `rg`, Python |
| `2` | Task failed / verify failed | Read error panel; check `verify_cmd` locally |

---

## `doctor` failures

### ripgrep not found

```bash
# Ubuntu/Debian
sudo apt install ripgrep

# macOS
brew install ripgrep
```

### LLM provider unreachable

```bash
code-agent env show
export GEMINI_API_KEY="..."
code-agent doctor --provider-test
```

Check model string in `config.yaml` (e.g. `gemini/gemini-2.0-flash`).

### PEP 668 pip blocked

Use a virtualenv:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

---

## `verify_cmd` keeps failing

1. Run the verify command **manually** in the same shell/env as the agent
2. Ensure project deps are installed in that venv
3. Pass the exact CI command: `--verify-cmd "pytest -q"` not a subset unless intentional
4. Check `max_iterations` in config (default 10)

---

## Expert `skipped`

| Reason | Meaning |
|--------|---------|
| `no actionable signals` | Log had no parseable errors — check parser support |
| `duplicate fingerprint` | Same failure within 24h — prior run exists |

---

## Expert `failed`

- Verify command exited non-zero after max iterations
- Safety policy blocked a write (forbidden path)
- Budget/throttle limit hit (platform mode)

Check `.code-agent/runs/<run_id>/` for `agent_state.json` and `trace.json`.

---

## `--publish` fails

| Issue | Fix |
|-------|-----|
| `gh` not found | Install and `gh auth login` |
| No git remote | `git remote -v` must show origin |
| Dirty tree conflicts | Commit or stash before publish |
| `require_approval` gate | Pass `--approve-publish` or approve in serve UI |

---

## Wrong workspace

Symptom: agent edits wrong repo or can't find tests.

```bash
code-agent run "..." -w /absolute/path/to/target-repo
```

Priority: CLI `-w` → `config.yaml` → `CODE_AGENT_WORKSPACE`.

---

## Go project + pytest mistake

Symptom: agent runs `pytest` on a Go repo.

Always set:

```bash
--verify-cmd "go test -v ./..." -w /path/to/go-repo
```

---

## Get help

- Artifacts: `.code-agent/runs/<run_id>/`
- Verbose: check `trace.json`, `signals.json`, `rca.json`
- Re-run with `--dry-run` first
