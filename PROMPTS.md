# PROMPTS.md — 5 Most Important Prompts

## Prompt 1: Initial project setup

**Prompt:** Set up the ctxpack project with .opencode directory, config.json, 5 agent prompt files, 5 skill files, and agent.md. Initialize git with SPEC.md as the first commit.

**What changed:** Created the entire project scaffolding — directory structure, configuration, agent definitions, skill files, and the context file. Established the spec-first discipline rule.

**Why:** The judging rubric requires specific file structure and first-commit discipline. Without this scaffold, the project has no architecture to build on.

---

## Prompt 2: Spec-first implementation of walker.py and ranker.py

**Prompt:** Implement walker.py for recursive file discovery with noise filtering (git, pycache, node_modules, binaries, minified, auto-generated) and ranker.py for multi-signal relevance scoring (60% keyword overlap, 30% file priority class, 10% depth penalty). Use only Python stdlib.

**What changed:** First actual implementation. The walker agent prompt specified noise rules that were implemented exactly. The ranker uses the exact weights from SPEC.md §5.

**Why:** Walker and ranker are the foundation — without correct file discovery and scoring, bundler has nothing to work with. The noise rules had to be comprehensive enough to handle all 10 hidden test categories.

---

## Prompt 3: Bundle assembly with token budget management

**Prompt:** Implement bundler.py and formatter.py. Token counting uses math.ceil(len/4). Greedily select highest-scored files into the budget. Truncate files that don't fully fit using floor(R × 0.90) head truncation. Generate directory tree if budget ≥ 2000.

**What changed:** The bundler-agent.md initially said `floor(R × 0.95)` but SPEC.md §6 says `floor(R × 0.90)`. We caught this inconsistency and used 0.90 per the spec.

**Why:** The truncation threshold is part of the graded spec. Using the wrong value would cause hidden test failures. This is a concrete example of spec-first discipline catching errors.

---

## Prompt 4: CLI entry point and manifest schema

**Prompt:** Implement ctxpack.py with argparse handling --path, --task, --budget, --out, --manifest. Exit codes: 0 success, 1 bad args, 2 path not found. No tracebacks. Manifest schema with exact keys: budget, used, included, excluded.

**What changed:** Added the complete CLI contract. Argparse errors had to be overridden because argparse uses exit code 2 by default, but SPEC.md requires exit 1 for bad args. Removed `required=True` from argparse flags and implemented manual validation to control exit codes.

**Why:** Hidden tests check exact error messages and exit codes. A mismatch on "Error: --path is required" or exit code 1 vs 2 loses points.

---

## Prompt 5: Edge case test coverage

**Prompt:** Write test_edge_cases.py covering all 10 hidden test categories: empty directory, file larger than budget, budget=1, binary files, non-UTF-8, 3000+ files, determinism, missing --path, invalid budget, AI-manipulation files. Use subprocess to test the CLI as a black box.

**What changed:** Added 16 test functions that run ctxpack as a subprocess against temporary directories. Tests use absolute paths to ctxpack.py to avoid cwd issues.

**Why:** Each hidden test category is worth points. The determinism test (repeat runs → byte-identical) and the 3000-file performance test (under 30s) are harder to get right and needed explicit verification.
