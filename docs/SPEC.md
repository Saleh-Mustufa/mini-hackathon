# SPEC.md — `ctxpack`

> Written before implementation. This document is a graded artifact.
> Updated entries are expected and visible in git history — updates show the spec was used, not just written.

**Version:** 1.0 — Initial spec (first commit)
**Status:** Pre-implementation

---

## 1. What This Tool Is

`ctxpack` is a Python 3.10+ command-line tool that solves the context window bottleneck for AI coding assistants.

Given a folder of code, a task description, and a token budget, it:
1. Discovers and scores every readable text file for relevance to the task
2. Packs the highest-scoring files into a single markdown bundle that fits inside the token budget
3. Produces a JSON manifest accounting for every file — included with its token cost and reason, excluded with the reason it was skipped

The output is designed to be pasted directly into an AI coding assistant as context.

---

## 2. CLI Contract

### Exact interface — hidden tests depend on this

```
ctxpack --path <folder> --task "<task description>" --budget <int> [--out <file>] [--manifest <file>]
```

### Flags

| Flag | Type | Required | Behavior |
|------|------|----------|----------|
| `--path` | string | Yes | Folder to pack. Must be an existing, readable directory. |
| `--task` | string | Yes | Free-text description of what the developer is trying to do. Used for relevance scoring. |
| `--budget` | int | Yes | Maximum tokens for the **entire** bundle output. Must be a positive integer. |
| `--out` | string | No | Write bundle to this file. If omitted, write to stdout. |
| `--manifest` | string | No | Write manifest JSON to this file. If omitted, print one-line summary to stderr. |

### Exit codes

| Code | Meaning | When |
|------|---------|------|
| `0` | Success | Bundle produced, manifest produced/printed |
| `1` | Invalid arguments | Missing required flag, non-integer budget, budget ≤ 0 |
| `2` | Path error | `--path` not found, not a directory, or unreadable |

### Error message contract

Every error produces **exactly one readable line to stderr**, then exits with the correct code. No raw tracebacks ever reach the user.

| Condition | Message |
|-----------|---------|
| `--path` missing | `Error: --path is required` |
| `--task` missing | `Error: --task is required` |
| `--budget` missing | `Error: --budget is required` |
| `--budget` not a positive integer | `Error: --budget must be a positive integer` |
| `--path` not found | `Error: path '<value>' not found or unreadable` |

The entire `main()` function is wrapped in a top-level `try/except Exception` to prevent any unhandled traceback from leaking. Internal errors print `Error: unexpected error — <message>` and exit 1.

---

## 3. Token Counting Rule

```python
import math

def count_tokens(text: str) -> int:
    return math.ceil(len(text) / 4)
```

**Scope:** This rule applies to the **complete bundle string** — every character, including headers, file path labels, separators, directory tree, code fences, and newlines. Not just the file contents.

**Why:** The brief specifies this rule explicitly so all teams count identically and results are comparable. We do not use tiktoken or any third-party library.

**Implication:** When assembling the bundle, we count tokens on the running string, not on individual files in isolation. A file that costs 400 tokens in isolation may cost slightly more in the bundle due to surrounding formatting.

---

## 4. Manifest Schema

The manifest accounts for **every file considered** — nothing is silently dropped.

```json
{
  "budget": 8000,
  "used": 7912,
  "included": [
    {
      "path": "src/ranker.py",
      "tokens": 812,
      "reason": "high keyword overlap with task, primary source file"
    }
  ],
  "excluded": [
    {
      "path": "package-lock.json",
      "reason": "noise: lockfile pattern detected"
    },
    {
      "path": "assets/logo.png",
      "reason": "binary file: null bytes detected"
    }
  ]
}
```

### Required keys

| Key | Type | Description |
|-----|------|-------------|
| `budget` | int | The `--budget` value passed in |
| `used` | int | Actual tokens in the final bundle |
| `included` | array | Every file added to the bundle |
| `excluded` | array | Every file considered and not included |

Each `included` entry: `path` (string, relative), `tokens` (int), `reason` (string).
Each `excluded` entry: `path` (string, relative), `reason` (string).

If `--manifest` is omitted, print this one-line summary to stderr:
```
ctxpack: X files included, Y excluded, Z/B tokens used
```

---

## 5. Ranking Strategy

### Decision: Weighted Multi-Signal Scoring

Each candidate file is scored 0–100 using three signals combined with fixed weights.

| Signal | Weight | Computation |
|--------|--------|-------------|
| **Keyword overlap** | 60% | Tokenize `--task` by splitting on whitespace and punctuation. Score = (matching tokens found in file path + first 50 lines of content) / total task tokens. Capped at 1.0. |
| **File priority class** | 30% | Assigned by extension and filename. See priority table below. |
| **Depth penalty** | 10% | Files at depth > 4 lose 10 points per extra level (min 0). |

**Final score:** `(keyword_score × 0.6) + (priority_score × 0.3) + (depth_score × 0.1)`

**Tie-breaking:** Alphabetical sort by path. This guarantees determinism when scores are equal.

#### Priority class table

| Class | Score | Files |
|-------|-------|-------|
| Entry points | 100 | `main.py`, `__main__.py`, `__init__.py`, `index.*`, `app.*`, `server.*` |
| Spec/docs | 90 | `*.md`, `*.rst`, `*.txt` (non-lockfile) |
| Source code | 70 | `*.py`, `*.js`, `*.ts`, `*.go`, `*.rs`, `*.java`, `*.c`, `*.cpp` |
| Config | 40 | `*.json`, `*.toml`, `*.yaml`, `*.yml`, `*.ini`, `*.cfg` |
| Data/other text | 20 | Everything else readable |

#### Why this approach over alternatives

| Alternative | Why Rejected |
|-------------|-------------|
| **Pure filename matching** | Too narrow — misses relevant files with generic names like `utils.py` or `helpers.js` that contain task-critical logic |
| **Import graph analysis** | Requires AST parsing (language-specific), fails on non-Python files, complex to implement correctly with stdlib only in 2 hours |
| **File recency (mtime)** | Recently modified ≠ relevant to the specific task; introduces non-determinism and environment sensitivity |
| **Full TF-IDF over file contents** | Correct approach but requires reading all files upfront — memory-expensive for 3000+ files; path + head scoring gives ~80% of the signal at ~10% of the cost |
| **Pure directory depth** | Shallower files are generally more architectural, but depth alone ignores the task entirely |

**Why this approach scores well:** It is deterministic, explainable (each file's score can be reproduced manually), fast (path-based scoring is O(n), content peek is bounded at 50 lines), and handles polyglot repos without language-specific parsing.

---

## 6. Truncation Policy

### When a file doesn't fit in the remaining budget

Let `R` = remaining budget tokens, `F` = file's token cost.

| Condition | Action |
|-----------|--------|
| `F ≤ R` | Include entire file |
| `F > R` AND `F ≤ 3 × R` | Include HEAD: first `floor(R × 0.90)` tokens of content, append `\n[TRUNCATED: showing X of Y tokens]` |
| `F > 3 × R` | Exclude entirely. Manifest reason: `"too large: F tokens, only R remaining"` |

### Why HEAD (not tail, not middle, not smart slice)

The head of a source file typically contains: module docstrings, imports, class declarations, function signatures, and constants — the structural skeleton. This is exactly what an AI assistant needs to understand what a file does. The tail is usually implementation detail.

Smart slicing (finding the most relevant section) would require content analysis, which is slower and less deterministic.

### Why the 3× threshold

If a file is more than 3× the remaining budget, including even 33% of it means the truncated version is still very large. The overhead tokens (header line, path label, code fence, truncation marker) become a disproportionate fraction of the remainder. It is more honest to exclude it entirely and use the budget for whole files that fit.

### Edge: file exactly equals remaining budget

Include it. The constraint is "never exceed budget" — matching exactly is valid.

---

## 7. Noise Detection

### Definition

Noise = any file that cannot contribute task-relevant signal, regardless of how it is named.

We use **pattern-based detection**, not a hardcoded name list. This matters because a hardcoded list (`["package-lock.json", "yarn.lock"]`) is brittle — it misses new tools (Bun's `bun.lockb`, Rust's `Cargo.lock`). Pattern-based detection catches unknown noise automatically.

### Automatic exclusions

| Pattern | Detection Method | Manifest Reason |
|---------|-----------------|-----------------|
| `.git/`, `.hg/`, `.svn/` | Path prefix check | `"version control internals"` |
| `__pycache__/`, `*.pyc`, `*.pyo` | Path segment / extension | `"Python bytecode"` |
| `node_modules/`, `vendor/` | Path segment | `"dependency tree"` |
| `dist/`, `build/`, `*.egg-info/` | Path segment | `"build artifact"` |
| Any `*.lock` file | Extension `.lock` | `"lockfile"` |
| `package-lock.json`, `yarn.lock` | Exact name | `"lockfile"` |
| Files with null bytes in first 8KB | Content scan | `"binary file"` |
| Files where >50% of first 10 lines exceed 300 chars | Content heuristic | `"minified or generated file"` |
| Files whose first line contains `generated by` or `auto-generated` (case-insensitive) | Content heuristic | `"auto-generated file"` |

### Unreadable files

Files that raise any exception during open or read are excluded with reason `"unreadable: <exception type>"`. This covers encoding errors, permission errors, and OS errors. The tool never crashes on a bad file.

For non-UTF-8 files that are otherwise readable, we attempt to read with `errors='ignore'`. If the result is empty or mostly replacement characters (>50% non-ASCII after decode), we exclude with reason `"non-text content"`.

---

## 8. Bundle Format

```
# ctxpack bundle
# Task: <task description>
# Budget: <N> tokens | Used: <N> tokens
# Generated: <ISO 8601 UTC timestamp>

## Project Structure
<directory tree, max 300 tokens>

---

## File: <relative/path/to/file.py>
<!-- tokens: N -->
```<extension>
<file content or truncated content>
```

---

## File: <relative/path/to/another.py>
<!-- tokens: N -->
```<extension>
<content>
```

---
```

### Directory tree

Include the project structure tree if `budget ≥ 2000`. Cap tree at 300 tokens by truncating after the token limit. The tree is generated from the walked file list (not `tree` shell command) to avoid any dependency.

**Why spend 300 tokens on the tree:** For a large codebase with thousands of files, the structural overview tells an AI assistant which directories exist and where to look. For tiny budgets (< 2000 tokens), every token counts for actual code.

**Why not always include it:** At very small budgets, 300 tokens is a significant fraction. Below 2000 tokens, we omit the tree and go straight to file content.

---

## 9. Determinism Guarantee

The same command run twice on the same folder produces byte-identical output.

**What makes output deterministic:**
- File ranking uses only: path string (deterministic), extension (deterministic), first 50 lines of content (read once, consistent)
- Tie-breaking: alphabetical sort by path — no hash-based, random, or mtime ordering anywhere
- Token counts: `math.ceil(len(text) / 4)` is a pure function
- Bundle assembly: greedy selection in fixed sort order

**The one non-deterministic element:** The `Generated:` timestamp in the bundle header. This does not affect content.

**For byte-identical output including the timestamp:** Set the `SOURCE_DATE_EPOCH` environment variable (standard Unix convention). ctxpack uses it if present: `datetime.fromtimestamp(int(os.environ['SOURCE_DATE_EPOCH']), tz=timezone.utc)`.

---

## 10. Architecture

```
ctxpack/
├── ctxpack.py       # CLI entry point — argparse, exit codes, orchestration
├── walker.py        # Recursive file discovery, noise filtering, metadata
├── ranker.py        # Multi-signal relevance scoring
├── bundler.py       # Token counting, budget management, truncation, assembly
├── manifest.py      # Manifest schema construction, JSON serialization
├── formatter.py     # Bundle markdown formatting, directory tree generation
├── test_edge_cases.py  # stdlib unittest covering all hidden test categories
├── SPEC.md          # This file
├── agent.md         # OpenCode context file (context engineering artifact)
├── PROMPTS.md       # 5 most important prompts with analysis
├── JOURNAL.md       # Five reflection questions
└── README.md        # Clone to first run in under 5 minutes
```

**All modules: Python 3.10+ standard library only.** No third-party imports anywhere.

### Module responsibilities

| Module | Inputs | Outputs |
|--------|--------|---------|
| `walker.py` | root path | list of `FileCandidate(path, size_bytes, depth, extension)` |
| `ranker.py` | list of `FileCandidate`, task string | sorted list of `ScoredFile(path, score, priority_class)` |
| `bundler.py` | sorted `ScoredFile` list, budget | `BundleResult(bundle_str, included, excluded, tokens_used)` |
| `manifest.py` | `BundleResult` | manifest dict, JSON string |
| `formatter.py` | file paths + content | formatted bundle sections, directory tree string |
| `ctxpack.py` | sys.argv | exit code, bundle to stdout/file, manifest to stderr/file |

---

## 11. Definition of Done

The tool is done when all of the following are true:

- [ ] All MUST requirements 1–7 pass against the hidden test categories
- [ ] SHOULD requirements 8–10 are implemented
- [ ] `ctxpack --path . --task "any task" --budget 8000` runs from a fresh clone in under 5 seconds on a 100-file repo
- [ ] Repeat runs produce byte-identical output (verified with md5/sha256)
- [ ] All hidden test categories have a corresponding local test in `test_edge_cases.py`
- [ ] First git commit contains only `SPEC.md` (verified with `git show --stat <first-commit-hash>`)
- [ ] `README.md` gets a judge from clone to first run in under 5 minutes
- [ ] `SPEC.md`, `agent.md`, `PROMPTS.md`, `JOURNAL.md` are complete and honest
- [ ] Every team member can explain any component when asked

---

## 12. Local Test Scenarios

Each maps to a hidden test category from the brief.

| Scenario | Expected Behavior |
|----------|------------------|
| Empty directory | Exit 0, bundle with zero included files, `used: 0` |
| Single file larger than entire budget | Truncation policy executes if `F ≤ 3R`, else excluded cleanly |
| Budget = 1 token | Bundle header alone may exceed budget — exit 0 with `used: N`, `included: []` |
| Binary file (.png, .exe) in folder | Excluded with `"binary file"` reason, no crash |
| Non-UTF-8 text file | Read with `errors='ignore'` or excluded, no crash |
| All files are noise | Exit 0, empty `included`, all files in `excluded` |
| 3000+ files | Completes in < 30 seconds |
| Repeat run same args | Output is byte-identical (diff or md5 check) |
| Missing `--path` | Exit 1, `Error: --path is required` on stderr |
| `--budget abc` | Exit 1, `Error: --budget must be a positive integer` on stderr |
| `--path /nonexistent` | Exit 2, `Error: path '/nonexistent' not found or unreadable` |
| `--out` to a file | Bundle written to file, not stdout |
| `--manifest` to a file | Valid JSON written to file matching schema exactly |

---

## 13. Decisions Made — for JOURNAL.md reference

### Decision 1: Ranking method
**Chose:** Weighted multi-signal (keyword + priority class + depth)
**Rejected:** Pure filename matching (too narrow), import graph (requires AST, stdlib-hard), file recency (irrelevant to task), full TF-IDF (memory-expensive for 3000 files)

### Decision 2: Truncation
**Chose:** HEAD truncation with 3× threshold for full exclusion
**Rejected:** Smart slice (non-deterministic, slow), tail (contains implementation not structure), skip-always (wastes usable budget)

### Decision 3: Noise detection
**Chose:** Pattern-based (extension, path segment, content heuristic)
**Rejected:** Hardcoded name list (brittle, misses new tools), no filtering (would pollute context with lockfiles and bytecode)

### Decision 4: Budget for directory tree
**Chose:** Include tree if budget ≥ 2000, cap at 300 tokens
**Rejected:** Always include (too expensive for tiny budgets), never include (loses structural overview for large repos)

---

*End of SPEC.md v1.0 — ready for first commit.*
