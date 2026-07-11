# kramlipi code-agent: AI That Fixes Code Until Your Tests Pass

**SEO title:** kramlipi code-agent: AI That Fixes Code Until Your Tests Pass  
**Meta description:** Fix failing unit tests and CI with kramlipi code-agent. It edits your repo, runs your verify command, and only stops when checks pass. Docker + one script—local Chat UI or your pipeline.

**kramlipi code-agent**

---

Most tools that claim to “fix CI with AI” do one of two things: they talk, or they hope.

kramlipi does a third thing. It changes your code, runs the check you already trust, and **refuses to call the job done until that check passes.**

That is the whole product.

---

## What you need

Three things. Nothing exotic.

1. **A Docker host** (laptop or CI runner) that can pull  
   `ghcr.io/kramlipi/code-agent:latest`
2. **An API key** for a model you already use — Gemini, OpenAI, Anthropic, or similar — set on the machine or as a CI secret (`GEMINI_API_KEY`, `OPENAI_API_KEY`, …)
3. **A project folder** and **a verify command** — the same command your pipeline already runs to decide pass or fail (`pytest -q`, `go test ./...`, `npm test`, …)

Optional: the one-file launcher `docker-ui.sh` if you want a browser UI on http://127.0.0.1:8080 instead of only the CLI.

```bash
# Linux / macOS / WSL
export GEMINI_API_KEY=your-key

curl -fsSL -o docker-ui.sh \
  https://gist.githubusercontent.com/kramlipi/d31f4f454cd127cfb552e5ed5e854af3/raw
chmod +x docker-ui.sh
bash docker-ui.sh
```

```powershell
# Windows PowerShell
$env:GEMINI_API_KEY = "your-key"

Invoke-WebRequest -Uri "https://gist.githubusercontent.com/kramlipi/387228f78eb47e437f578f625a101707/raw" `
  -OutFile docker-ui.ps1
.\docker-ui.ps1
```

Gists: [Linux `docker-ui.sh`](https://gist.github.com/kramlipi/d31f4f454cd127cfb552e5ed5e854af3) · [Windows `docker-ui.ps1`](https://gist.github.com/kramlipi/387228f78eb47e437f578f625a101707)

Open the UI, choose a folder on your machine, and work.  
Or skip the UI and run the image in CI the same way you run any other container.

---

## What it does

In plain language:

- **Fixes failing unit tests** until your test command is green  
- **Fixes build, type, and lint failures** the same way — against *your* gate  
- **Raises coverage** by adding tests when a coverage gate fails — not by deleting product code  
- **Takes a failed CI log** and produces a real fix in the repo, not a summary in Slack  
- **Opens a draft pull request** when you ask it to publish, so someone can review in the morning  
- **Babysits a PR** that keeps going red — repairs the same branch and lets CI run again  
- **Shortens PR test runs** by selecting only the tests that matter for the change  
- **Finds missing metrics** on handlers and can open an MR for instrumentation  
- **Responds after deploy or to an alert** with the same rule: change code, prove it, or stop  

It does **not** replace GitHub Actions, GitLab, Jenkins, or CircleCI.  
It sits **beside** them. Your runners still run. Your gates still decide. kramlipi proposes edits; the environment keeps the score.

It will **not** rewrite your workflow YAML to fake a green check. That is deliberate.

---

## How it does it

The loop is short on purpose.

1. **Intake** — a prompt, a CI log, a PR that failed, or an alert  
2. **Understand** — structured reading of the failure (what broke, where), not vibes  
3. **Edit** — real files in the project you pointed it at  
4. **Verify** — run the command you named  
5. **Decide** — exit code `0` → done (and optionally draft PR); anything else → try again or fail honestly  

The model suggests.  
**Your verify command decides.**

Same image on a laptop and in a pipeline. Same key. Same rule.  
Local tonight: UI or CLI. Pipeline tomorrow: a step on failure, a follow-up job, a nightly, or a PR babysit — mount the repo, pass the key, pass the verify command.

---

## Where it sits in a pipeline

Think of it as a worker that only speaks when it has proof.

**When a job fails**  
Feed it the log (or a webhook). It edits the app, re-runs your verify command, and can open a draft PR. Duplicate failures that already have a fix in flight can be skipped.

**When a PR keeps failing**  
Point it at the PR. It fixes on that branch, within a retry limit, and pushes so CI runs again. You still merge.

**When CI is too slow**  
Ask it for the tests that match the diff. Put that shorter command in the PR job. Fall back to the full suite when selection doesn’t apply.

**When a quality gate fails**  
Same loop — tests, build, lint, coverage — always against the command you already trust.

**After release or when ops pages you**  
Health or metrics look wrong, or an alert fires: attempt a fix, prove it, or stop. No victory speech without a passing check.

**What the pipeline must provide**  
The image, the secret, the checkout, and the verify command. That is the contract.

---

## The honest pitch

Conversation is cheap.  
Consequence is not.

kramlipi is for teams who are tired of AI that *sounds* finished while CI is still red.

**What it does:** fix real code and prove it.  
**How it does it:** edit → run your check → repeat or stop.  
**What it needs:** Docker, a model key, a project, and a verify command.

```bash
export GEMINI_API_KEY=…
bash docker-ui.sh
```

One image. One script if you want the UI. One rule: **prove it.**

---

*kramlipi code-agent — it doesn’t get to declare victory. Your tests do.*
