"""Merge kramlipi docs into 5-tab nav pages without losing content."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"


def strip_front_matter(text: str) -> str:
    if text.startswith("---"):
        end = text.find("---", 3)
        if end != -1:
            return text[end + 3 :].lstrip("\n")
    return text


def strip_h1(text: str) -> str:
    lines = text.splitlines()
    out: list[str] = []
    skipped = False
    for line in lines:
        if not skipped and line.startswith("# ") and not line.startswith("## "):
            skipped = True
            continue
        out.append(line)
    return "\n".join(out).lstrip("\n")


def load_body(name: str) -> str:
    return strip_h1(strip_front_matter((DOCS / name).read_text(encoding="utf-8")))


def banner(target: str) -> str:
    return (
        f"!!! info \"Also on merged page\"\n"
        f"    Full content below is preserved. Same section: [{target}]({target}).\n\n"
    )


def build_features() -> None:
    parts = [
        """---
title: Features
description: >-
  code-agent experts, CLI commands, copy-paste recipes, and coverage runbook —
  full reference merged on one page.
keywords: code-agent features, experts, cli, recipes, coverage, verify-cmd
---

# Features

Everything **code-agent** can do — experts, CLI, recipes, and coverage.  
Pain-first walkthroughs live on **[Use cases](use-cases.md)**.

---

## Experts {#experts}

""",
        load_body("experts.md"),
        "\n\n---\n\n## CLI commands {#commands}\n\n",
        load_body("commands.md"),
        "\n\n---\n\n## Recipes {#recipes}\n\n",
        load_body("recipes.md"),
        "\n\n---\n\n## Coverage {#coverage}\n\n",
        load_body("coverage.md"),
    ]
    (DOCS / "features.md").write_text("".join(parts), encoding="utf-8")


def build_use_cases() -> None:
    uc_body = load_body("use-cases.md")
    intro = """---
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

"""
    out = intro + uc_body
    out += "\n\n---\n\n## Developer & DevOps pains catalog {#pains-catalog}\n\n"
    out += load_body("pains.md")
    out += "\n\n---\n\n## Language walkthroughs {#language-walkthroughs}\n\n"
    out += "### Python — failing unit tests {#python-example}\n\n"
    out += load_body("examples/python.md")
    out += "\n\n### Go — failing unit tests {#go-example}\n\n"
    out += load_body("examples/go.md")
    out += "\n\n### Java — failing unit tests {#java-example}\n\n"
    out += load_body("examples/java.md")
    (DOCS / "use-cases.md").write_text(out, encoding="utf-8")


def add_banners() -> None:
    mapping = {
        "experts.md": "features.md#experts",
        "commands.md": "features.md#commands",
        "recipes.md": "features.md#recipes",
        "coverage.md": "features.md#coverage",
        "pains.md": "use-cases.md#pains-catalog",
        "examples/python.md": "use-cases.md#python-example",
        "examples/go.md": "use-cases.md#go-example",
        "examples/java.md": "use-cases.md#java-example",
    }
    for rel, target in mapping.items():
        path = DOCS / rel
        text = path.read_text(encoding="utf-8")
        if "Also on merged page" in text:
            continue
        end = text.find("---", 3) + 3 if text.startswith("---") else 0
        if end:
            updated = text[:end] + "\n\n" + banner(target) + text[end:].lstrip("\n")
        else:
            updated = banner(target) + text
        path.write_text(updated, encoding="utf-8")


def main() -> None:
    build_features()
    build_use_cases()
    add_banners()
    print("OK: features.md", len((DOCS / "features.md").read_text().splitlines()), "lines")
    print("OK: use-cases.md", len((DOCS / "use-cases.md").read_text().splitlines()), "lines")


if __name__ == "__main__":
    main()
