---
title: Add code-review to CI
description: >-
  Copy-paste GitHub Actions, GitLab CI, and Azure Pipelines to run kramlipi
  code-review on every PR/MR. Downloads the Linux binary from Releases.
keywords: >-
  code review CI, GitHub Actions code review, GitLab CI review, Azure DevOps
  PR review, kramlipi code-agent
---

# Add code-review agent to CI (copy-paste)

**Binary releases:** https://github.com/kramlipi/code-agent-binaries/releases  
**Docs:** https://kramlipi.github.io/code-review-ci/  
**Contact:** cluevion@gmail.com

Wire `code-review` so every PR/MR gets a first-pass review (SOLID + security smells, line findings).

| Platform | Posts inline comments | How |
|----------|----------------------|-----|
| **GitHub Actions** | Yes (`gh` API) | `--pr N` |
| **GitLab CI** | Summary note on the MR | `--diff-file` + `glab mr note` |
| **Azure DevOps** | Summary comment on the PR | `--diff-file` + REST API |

Secrets / variables needed on all platforms:

| Name | Purpose |
|------|---------|
| `GEMINI_API_KEY` | LLM key ([AI Studio](https://aistudio.google.com/)) |
| `CODE_AGENT_MODEL` | Optional; default `gemini/gemini-3.1-flash-lite` |

Economy mode is **off by default** (full quality). To save cost: `CODE_AGENT_ECONOMY_MODE=true`.

---

## GitHub Actions — copy-paste

Save as `.github/workflows/code-review.yml`:

```yaml
name: PR Code Review (kramlipi)

on:
  pull_request:
    types: [opened, synchronize, reopened]

permissions:
  contents: read
  pull-requests: write

jobs:
  code-review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Install ripgrep
        run: sudo apt-get update && sudo apt-get install -y ripgrep

      - name: Download code-agent (Linux)
        env:
          GH_TOKEN: ${{ github.token }}
        run: |
          set -euo pipefail
          TAG="$(gh release list --repo kramlipi/code-agent-binaries --limit 1 --json tagName -q '.[0].tagName')"
          # tag is code-agent-vX.Y.Z → asset uses vX.Y.Z
          VER="${TAG#code-agent-}"
          gh release download "$TAG" \
            --repo kramlipi/code-agent-binaries \
            --pattern "code-agent-${VER}-linux" \
            --dir /tmp
          install -m 755 "/tmp/code-agent-${VER}-linux" /usr/local/bin/code-agent
          code-agent --help | head -5

      - name: Review PR (inline comments)
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
          CODE_AGENT_MODEL: gemini/gemini-3.1-flash-lite
        run: |
          code-agent experts run code-review \
            --pr ${{ github.event.pull_request.number }} \
            -w .
```

**Optional dry-run (no posts):** add `--dry-run` to the command.

**Docker alternative:**

```yaml
      - name: Review PR via GHCR
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
          CODE_AGENT_MODEL: gemini/gemini-3.1-flash-lite
        run: |
          docker run --rm \
            -e GH_TOKEN -e GEMINI_API_KEY -e CODE_AGENT_MODEL \
            -v "$PWD:/workspace" -w /workspace \
            ghcr.io/kramlipi/code-agent:latest \
            experts run code-review \
              --pr ${{ github.event.pull_request.number }} \
              -w /workspace
```

---

## GitLab CI — copy-paste

Save as `.gitlab-ci.yml` job (or include in an existing file).

**CI/CD variables:** `GEMINI_API_KEY` (masked). Optional: `CODE_AGENT_MODEL`.

```yaml
stages:
  - review

code-review:
  stage: review
  image: ubuntu:24.04
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
  before_script:
    - apt-get update -qq && apt-get install -y -qq curl ca-certificates git ripgrep
    - |
      set -euo pipefail
      TAG=$(curl -fsSL \
        "https://api.github.com/repos/kramlipi/code-agent-binaries/releases/latest" \
        | sed -n 's/.*"tag_name": *"\([^"]*\)".*/\1/p' | head -1)
      VER="${TAG#code-agent-}"
      curl -fsSL -o /usr/local/bin/code-agent \
        "https://github.com/kramlipi/code-agent-binaries/releases/download/${TAG}/code-agent-${VER}-linux"
      chmod +x /usr/local/bin/code-agent
  script:
    - git fetch origin "${CI_MERGE_REQUEST_TARGET_BRANCH_NAME}" --depth=50 || true
    - git diff "origin/${CI_MERGE_REQUEST_TARGET_BRANCH_NAME}...HEAD" > /tmp/mr.diff
    - |
      export CODE_AGENT_MODEL="${CODE_AGENT_MODEL:-gemini/gemini-3.1-flash-lite}"
      code-agent experts run code-review \
        --diff-file /tmp/mr.diff \
        -w .
    - |
      # Post a summary note on the MR (findings JSON from latest run)
      FINDINGS=$(ls -1d .code-agent/runs/*/review-findings.json 2>/dev/null | tail -1 || true)
      if [ -n "$FINDINGS" ] && command -v glab >/dev/null 2>&1; then
        glab mr note "$CI_MERGE_REQUEST_IID" --message "$(
          printf '### kramlipi code-review\n\n```json\n%s\n```\n' "$(cat "$FINDINGS")"
        )" || true
      elif [ -n "$FINDINGS" ]; then
        echo "Findings artifact: $FINDINGS"
        head -c 4000 "$FINDINGS" || true
      fi
  artifacts:
    when: always
    paths:
      - .code-agent/runs/
    expire_in: 7 days
```

Install [`glab`](https://gitlab.com/gitlab-org/cli) in `before_script` if you want the MR note auto-posted.

---

## Azure DevOps — copy-paste

Save as `azure-pipelines-code-review.yml` (same content as [`ci/azure-pipelines-code-review.yml`](code-review-ci.md#azure-devops--copy-paste)).

**Pipeline variables / variable group:** `GEMINI_API_KEY` (secret).

```yaml
trigger: none

pr:
  branches:
    include:
      - "*"

pool:
  vmImage: ubuntu-latest

steps:
  - checkout: self
    fetchDepth: 0

  - bash: |
      set -euo pipefail
      sudo apt-get update -qq && sudo apt-get install -y -qq ripgrep curl ca-certificates
      TAG=$(curl -fsSL \
        "https://api.github.com/repos/kramlipi/code-agent-binaries/releases/latest" \
        | sed -n 's/.*"tag_name": *"\([^"]*\)".*/\1/p' | head -1)
      VER="${TAG#code-agent-}"
      curl -fsSL -o /usr/local/bin/code-agent \
        "https://github.com/kramlipi/code-agent-binaries/releases/download/${TAG}/code-agent-${VER}-linux"
      chmod +x /usr/local/bin/code-agent
    displayName: Install code-agent binary

  - bash: |
      set -euo pipefail
      TARGET="${SYSTEM_PULLREQUEST_TARGETBRANCH:-main}"
      TARGET="${TARGET#refs/heads/}"
      git fetch origin "$TARGET" --depth=50 || true
      git diff "origin/${TARGET}...HEAD" > /tmp/pr.diff
      export CODE_AGENT_MODEL="${CODE_AGENT_MODEL:-gemini/gemini-3.1-flash-lite}"
      code-agent experts run code-review --diff-file /tmp/pr.diff -w .
    displayName: Run code-review
    env:
      GEMINI_API_KEY: $(GEMINI_API_KEY)

  - task: PublishPipelineArtifact@1
    inputs:
      targetPath: .code-agent/runs
      artifact: code-review-findings
    condition: always()
```

Findings land under `.code-agent/runs/*/review-findings.json` (pipeline artifact). Inline GitHub-style threads are GitHub-only today; Azure gets the artifact + optional REST comment (see full guide on the site).

---

## Local one-liners

```bash
# GitHub PR — post inline comments
export GEMINI_API_KEY=...
export GH_TOKEN=...   # or gh auth login
code-agent experts run code-review --pr 42 -w .

# Preview only
code-agent experts run code-review --pr 42 --dry-run -w .

# Any platform — review a unified diff (findings on disk, no GitHub post)
git diff main...HEAD > /tmp/mr.diff
code-agent experts run code-review --diff-file /tmp/mr.diff -w .
```

---

## Related

- Product templates: `.github/workflows/code-review-template.yml`
- Expert flags: [TASKS-AND-EXPERTS.md](./TASKS-AND-EXPERTS.md#5-expert-code-review)
- Quick start: [QUICKSTART.md](quick-start.md)
