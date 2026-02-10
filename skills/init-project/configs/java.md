# Java Configs

## Editor Config additions

```ini
[*.{java,kt,kts}]
indent_size = 4
```

## mise.toml (Gradle)

```toml
[tools]
java = "zulu-21"
"npm:prettier" = "latest"
"npm:markdownlint-cli2" = "latest"

[tasks.fmt]
description = "Format all files"
run = """
#!/usr/bin/env bash
set -euo pipefail
./gradlew spotlessApply
prettier --write "**/*.{md,json,yaml,yml}"
"""

[tasks.fmt-check]
description = "Check formatting"
run = """
#!/usr/bin/env bash
set -euo pipefail
./gradlew spotlessCheck
prettier --check "**/*.{md,json,yaml,yml}"
"""

[tasks.test]
description = "Run tests"
run = "./gradlew test"

[tasks.build]
description = "Build the project"
run = "./gradlew build"

[tasks.check]
description = "Run all checks"
depends = ["fmt-check", "test"]
```

## mise.toml (Maven)

```toml
[tools]
java = "zulu-21"
"npm:prettier" = "latest"
"npm:markdownlint-cli2" = "latest"

[tasks.fmt]
description = "Format all files"
run = """
#!/usr/bin/env bash
set -euo pipefail
mvn spotless:apply
prettier --write "**/*.{md,json,yaml,yml}"
"""

[tasks.fmt-check]
description = "Check formatting"
run = """
#!/usr/bin/env bash
set -euo pipefail
mvn spotless:check
prettier --check "**/*.{md,json,yaml,yml}"
"""

[tasks.test]
description = "Run tests"
run = "mvn test"

[tasks.build]
description = "Build the project"
run = "mvn package -DskipTests"

[tasks.check]
description = "Run all checks"
depends = ["fmt-check", "test"]
```

## Makefile (Gradle)

```makefile
.PHONY: fmt fmt-check lint test build check clean

fmt:
	./gradlew spotlessApply

fmt-check:
	./gradlew spotlessCheck

lint: fmt-check

test:
	./gradlew test

build:
	./gradlew build

check: fmt-check test

clean:
	./gradlew clean
```

## CI steps (non-mise)

```yaml
- uses: actions/setup-java@v4
  with:
    distribution: temurin
    java-version: 21
- uses: gradle/actions/setup-gradle@v4
- run: ./gradlew check
```

## .gitignore additions

```gitignore
build/
.gradle/
*.class
target/
```
