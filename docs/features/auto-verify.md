---
title: Auto verify — no need to guess pytest vs mvn vs go test
description: >-
  code-agent detects your project language and picks the verify command automatically.
  Optional --verify-cmd override. Seventeen industry stacks supported.
---

# Auto verify (optional `--verify-cmd`)

**Public URL:** https://kramlipi.github.io/features/auto-verify/

Nobody should have to memorize `pytest -q` vs `mvn test -q` vs `go test ./...` before their first agent run.

**code-agent** opens your repo folder, figures out the stack, picks a **verify command**, runs it, and only marks the job **done** when that command exits **0**. You see exactly what we run — before and after the agent loop.

`--verify-cmd` is **optional**. Pass it only when you want to override auto-detection.

---

## Quick start (no verify flag)

```bash
export GEMINI_API_KEY=...
cd /path/to/your-repo

code-agent run "fix failing unit tests" -w .
```

Before the agent starts you’ll see something like:

```text
Auto-detected verify command from this project — we run this and require exit 0:
  mvn -q test
  (pom.xml detected)
```

Preview without spending an LLM call:

```bash
code-agent doctor --verify-plan "fix failing unit tests" -w .
```

---

## What we detect (17 industry stacks)

| Language / stack | We look for | Default verify |
|------------------|-------------|----------------|
| **Python** | `pyproject.toml`, `requirements.txt`, `setup.py`, `pytest.ini` | `pytest -q` |
| **JavaScript / TypeScript** | `package.json` | `npm test` |
| **Go** | `go.mod`, `.go` sources | `go test ./...` |
| **Rust** | `Cargo.toml` | `cargo test` |
| **Java (Maven)** | `pom.xml` | `mvn -q test` |
| **Java / Kotlin (Gradle)** | `build.gradle`, `gradlew` | `./gradlew test` or `gradle test` |
| **C# / .NET** | `*.csproj`, `*.sln` | `dotnet test` |
| **Ruby** | `Gemfile` | `bundle exec rspec` (or `rake test`) |
| **PHP** | `composer.json` | `composer test` / `vendor/bin/phpunit` |
| **Swift** | `Package.swift` | `swift test` |
| **Scala** | `build.sbt` | `sbt test` |
| **Dart / Flutter** | `pubspec.yaml` | `dart test` or `flutter test` |
| **Elixir** | `mix.exs` | `mix test` |
| **Clojure** | `deps.edn`, `project.clj` | `clojure -M:test` / `lein test` |
| **Haskell** | `stack.yaml`, `*.cabal` | `stack test` / `cabal test` |
| **C / C++** | `CMakeLists.txt` | `ctest --output-on-failure` |
| **Perl** | `cpanfile`, `Makefile.PL` | `prove -lr t` |
| **R** | `DESCRIPTION` | `testthat` via `Rscript` |

Coverage and lint intents get stack-aware commands too (e.g. Python coverage → `pytest --cov=…`, Node lint → `npm run lint`).

---

## How picking works (priority)

```text
1. Your --verify-cmd or config verify_cmd     → always wins
2. Words in your task ("mvn test", "dotnet")   → toolchain override
3. CI workflow test steps (.github/workflows) → same command CI uses
4. Project manifest (pom.xml, go.mod, …)      → stack default
5. Makefile test / check target               → make test
6. Majority source language in the tree       → when no manifest at root
```

We **tell you** the resolved command in the CLI banner and again in the result panel (`Verify: \`…\``).

Experts (`bug-fix`, `coverage-growth`, `flake`, …) use the same resolver when you omit `--verify-cmd`.

---

## Examples by stack

### Java / Maven

```bash
cd my-spring-app
code-agent run "fix failing unit tests" -w .
# → mvn -q test
```

### .NET

```bash
cd my-api
code-agent experts run bug-fix --log /tmp/ci.log -w .
# → dotnet test
```

### Ruby

```bash
cd my-rails-app
code-agent run "fix failing specs" -w .
# → bundle exec rspec
```

### Polyglot monorepo

Say the stack in the task if the wrong manifest wins at repo root:

```bash
code-agent run "fix the Go packages only" -w .
# task wording "go test" → go test ./...
```

---

## Override when you want to

```bash
code-agent run "fix tests" -w . --verify-cmd "mvn test -q"
```

Or in `config.yaml`:

```yaml
auto_verify: true          # default
# verify_cmd: "custom cmd"  # optional global override
```

Turn off auto-detection entirely:

```yaml
auto_verify: false
verify_cmd: "pytest -q"
```

---

## What we don’t promise

| Gap | Notes |
|-----|--------|
| **Toolchain install** | `mvn`, `dotnet`, `flutter`, etc. must exist on your machine or CI runner |
| **Every niche language** | COBOL, Fortran, custom embedded flows — pass `--verify-cmd` |
| **Xcode schemes** | No automatic `xcodebuild` scheme pick yet; use explicit verify |
| **Polyglot edge cases** | Manifest priority may not match your mental “primary” language — override with flags or task wording |

---

## VS Code panel

The Agent panel auto-detects verify from manifests and majority language (same idea as CLI). Click **↻** to refresh, or type a command if detection fails.

---

## Related

- [Get started](../get-started.md) — binary, API key, first run  
- [Features → verify]((index.md#how-to-use-verify-commands)) — copy-paste by language  
- [Commands](../commands.md) — full CLI reference  
- [Use cases](../use-cases.md) — pain → command  
- Product source: `language_stacks.py`, `verify_resolver.py`

**Try free:** https://kramlipi.github.io/get-started/ · **Contact:** cluevion@gmail.com
