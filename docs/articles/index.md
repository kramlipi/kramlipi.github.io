---
title: Tutorials & Blog — Kramlipi code-agent
description: >-
  Step-by-step tutorials and blog posts — verify-gated AI that only stops when
  your command exits 0.
keywords: tutorials, blog, code-agent, test-intel, pytest, go test, coverage, code review
---

# Tutorials & Blog

Short stories. Real commands. Your verify command keeps the score.

Use the **Tutorials & Blog** tab in the top navigation to browse posts. When you open an article, the left sidebar lists every tutorial and the right rail shows **On this page** — same layout pattern as modern docs sites (CodeRabbit, Stripe, etc.).

<div class="kl-blog-grid">

<a class="kl-blog-card" href="smarter-testing-m1-test-intel.md">
<span class="kl-tag">New · test-intel</span>
<h3>Smarter Testing M1 — run only impacted tests</h3>
<p>Doc-only PRs skip the suite. Coverage contexts pick tests. Same-SHA flake memory. JUnit timings for shards.</p>
</a>

<a class="kl-blog-card" href="tutorial-python-failing-tests.md">
<span class="kl-tag">Python</span>
<h3>Fix failing pytest until green</h3>
<p>Build a broken repo, run bug-fix with verify_cmd, and refuse to stop until pytest exits 0.</p>
</a>

<a class="kl-blog-card" href="tutorial-go-failing-tests.md">
<span class="kl-tag">Go</span>
<h3>Fix failing go test</h3>
<p>When CI prints --- FAIL, let the agent patch and re-run your exact test command.</p>
</a>

<a class="kl-blog-card" href="tutorial-java-failing-tests.md">
<span class="kl-tag">Java</span>
<h3>Fix Maven / Gradle tests</h3>
<p>BUILD FAILURE in CI — parse, fix, verify with the same Maven command.</p>
</a>

<a class="kl-blog-card" href="tutorial-raise-coverage.md">
<span class="kl-tag">Coverage</span>
<h3>Raise coverage without cheating</h3>
<p>Coverage gate blocks merge — add real tests until your verify command passes.</p>
</a>

<a class="kl-blog-card" href="tutorial-bugfix-ci-log.md">
<span class="kl-tag">bug-fix</span>
<h3>Bug-fix from a CI log</h3>
<p>3,000-line log archaeology — scoped repair with objective verify.</p>
</a>

<a class="kl-blog-card" href="tutorial-pr-code-review.md">
<span class="kl-tag">code-review</span>
<h3>PR line-comment code review</h3>
<p>First-pass review with repo context — not a chatbot paraphrase of the diff.</p>
</a>

<a class="kl-blog-card" href="tutorial-ultra-intelligence-missing-go.md">
<span class="kl-tag">cascade</span>
<h3>Ultra intelligence — missing Go</h3>
<p>go: command not found — env diagnose before code edits.</p>
</a>

<a class="kl-blog-card" href="the-computer-that-doesnt-guess.md">
<span class="kl-tag">Essay</span>
<h3>AI that doesn't guess</h3>
<p>Edits your repo, runs your check, refuses to call the job done until verify passes.</p>
</a>

</div>

## All tutorials (table)

| Tutorial | Pain | Type |
|----------|------|------|
| [Smarter Testing M1](smarter-testing-m1-test-intel.md) | Full suite on every PR | test-intel |
| [Python: fix a failing pytest](tutorial-python-failing-tests.md) | Red unit test at midnight | Python |
| [Go: fix a failing `go test`](tutorial-go-failing-tests.md) | `--- FAIL:` in CI | Go |
| [Java: fix Maven / Gradle tests](tutorial-java-failing-tests.md) | BUILD FAILURE | Java |
| [Raise coverage without cheating](tutorial-raise-coverage.md) | Coverage gate blocks merge | Coverage |
| [Bug-fix from a CI log](tutorial-bugfix-ci-log.md) | Log archaeology | bug-fix |
| [PR line-comment code review](tutorial-pr-code-review.md) | No first-pass on every PR | code-review |
| [Ultra intelligence: missing Go](tutorial-ultra-intelligence-missing-go.md) | `go: command not found` | cascade |
| [AI that doesn't guess](the-computer-that-doesnt-guess.md) | Agents that talk, not fix | Essay |

**Start here:** [Quick Start](../quick-start.md) · **Contact:** cluevion@gmail.com
