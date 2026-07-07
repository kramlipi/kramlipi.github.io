---
title: Java — Failing Unit Tests
description: >-
  Create a failing JUnit test with Maven or Gradle, fix with code-agent using
  mvn test or gradlew test verify-cmd.
keywords: java junit, maven test, gradle test, code-agent failing unit test
---

# Java — Failing Unit Test Example

Java uses **JUnit** + **Maven** or **Gradle**. Set `--verify-cmd` to match your build tool.

!!! info "Parser note"
    Dedicated Java/JUnit log parser is limited — `bug-fix` uses **generic error parsing** plus the agent reading test output. **`--verify-cmd` is critical** so the agent proves `mvn test` or `./gradlew test` passes.

---

## Option A — Maven project

### 1. Create a failing test

```bash
mkdir -p /tmp/java-demo && cd /tmp/java-demo
git init

mvn archetype:generate -DgroupId=com.example -DartifactId=demo \
  -DarchetypeArtifactId=maven-archetype-quickstart -DinteractiveMode=false

cd demo

# Introduce bug in main code
cat > src/main/java/com/example/App.java <<'EOF'
package com.example;

public class App {
    public static int add(int a, int b) {
        return a - b; // BUG: should be +
    }
}
EOF

cat > src/test/java/com/example/AppTest.java <<'EOF'
package com.example;

import org.junit.Test;
import static org.junit.Assert.*;

public class AppTest {
    @Test
    public void testAdd() {
        assertEquals(5, App.add(2, 3));
    }
}
EOF

mvn test
```

**Expected:** `BUILD FAILURE` with assertion error in output.

**Save log:**

```bash
mvn test 2>&1 | tee /tmp/java-maven.log
```

### 2. Fix with code-agent

```bash
source /path/to/ai-code-agent/.venv/bin/activate

code-agent run \
  "Fix failing AppTest. The add method in App.java returns wrong result. Run 'mvn test' until BUILD SUCCESS. Change only what is needed." \
  --verify-cmd "mvn test -q" \
  -w /tmp/java-demo/demo
```

### 3. Fix with bug-fix expert

```bash
code-agent experts run bug-fix \
  --log /tmp/java-maven.log \
  --verify-cmd "mvn test -q" \
  -w /tmp/java-demo/demo
```

### Flags explained

| Flag | Value | Why |
|------|-------|-----|
| `-w` | Maven module root (`pom.xml` here) | Agent edits `src/main` and `src/test` |
| `--verify-cmd` | `mvn test -q` | Must match CI — quiet Maven like Actions |
| `--log` | Maven surefire output | Failure class + line from log |

---

## Option B — Gradle project

### 1. Create project + failing test

```bash
mkdir -p /tmp/gradle-demo && cd /tmp/gradle-demo
git init

gradle init --type java-application --dsl kotlin --test-framework junit-jupiter --package com.example --project-name demo
cd demo

# Edit generated code to fail (similar App class + test)
./gradlew test
```

**Save log:**

```bash
./gradlew test 2>&1 | tee /tmp/java-gradle.log
```

### 2. Fix with code-agent

```bash
code-agent experts run bug-fix \
  --log /tmp/java-gradle.log \
  --verify-cmd "./gradlew test" \
  -w /tmp/gradle-demo/demo
```

| Flag | Why |
|------|-----|
| `--verify-cmd "./gradlew test"` | Gradle wrapper — same as CI |
| `-w` | Directory with `build.gradle.kts` |

---

## Add missing unit tests (coverage)

For Java coverage (JaCoCo), use verify command that includes coverage gate:

```bash
# Example — adjust to your pom.xml / build.gradle
mvn test jacoco:report 2>&1 | tee /tmp/java-cov.log

code-agent experts run bug-fix \
  --log /tmp/java-cov.log \
  --verify-cmd "mvn test jacoco:report" \
  -w /path/to/java-project
```

Agent adds tests under `src/test/java/` for uncovered methods.

---

## Open merge request

```bash
code-agent experts run bug-fix \
  --log /tmp/java-maven.log \
  --verify-cmd "mvn test -q" \
  -w /path/to/java-project \
  --publish \
  --base-branch main
```

| Flag | Meaning |
|------|---------|
| `--publish` | Creates branch + draft PR with fix |
| `--base-branch` | Target branch for MR |

Requires `gh auth login`.

---

## Common mistakes

| Mistake | Fix |
|---------|-----|
| `-w` at wrong level | Must be folder with `pom.xml` or `build.gradle` |
| `mvn test` vs `mvn verify` | Use **exact** CI command in `--verify-cmd` |
| JDK not installed | Install JDK 17+; `java -version` must work |
| Mixing Maven and Gradle flags | Pick one build tool per project |

[← Back to Quick Start](../quick-start.md)
