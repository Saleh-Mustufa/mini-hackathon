# 🧰 ctxpack

**Context Packer** — Pack the most relevant files from any codebase into one markdown bundle that fits your AI assistant's context window.

![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![stdlib](https://img.shields.io/badge/stdlib--only-green)
![no pip](https://img.shields.io/badge/pip-free-orange)
![license](https://img.shields.io/badge/license-MIT-lightgrey)

---

## Table of Contents

- [What is ctxpack?](#what-is-ctxpack)
- [Agentic AI Integration](#-agentic-ai-integration)
- [Quick Start](#quick-start)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Examples](#examples)
- [Sample Output](#sample-output)
- [Exit Codes](#exit-codes)
- [How It Works](#how-it-works)
- [Token Counting](#token-counting)
- [Bundle Format](#bundle-format)
- [Determinism](#determinism)
- [Noise Filtering](#noise-filtering)
- [AI Agent Skill](#ai-agent-skill)
- [Tips & Best Practices](#tips--best-practices)
- [Project Structure](#project-structure)

---

## What is ctxpack?

ctxpack scans a codebase folder, scores every file for relevance to your task, and packs the best ones into a single markdown document that fits inside a token budget.

**The problem it solves:** AI coding assistants have context window limits (typically 8K–200K tokens). You can't paste your entire project. ctxpack selects the *most relevant* files automatically so your AI assistant sees exactly what it needs.

**Where to use it:**
- Before sending a prompt to Claude, GPT, Copilot, or any AI coding assistant
- Code review preparation — give the reviewer/AI only what matters
- Onboarding — pack the architectural core of an unfamiliar project
- Bug fixing — ctxpack automatically finds files related to the bug area

---

## 🤖 Agentic AI Integration

ctxpack is purpose-built to fuel **agentic AI coding tools** — Claude Code, OpenCode, Codex CLI, Copilot CLI, Cursor, Windsurf, and others.

### Why agentic tools need ctxpack

Agentic AI tools consume context tokens for everything: reading files, searching directories, understanding structure. Every token spent on **discovery** is a token not spent on **reasoning** or **code generation**.

ctxpack solves this by doing the discovery *before* the agent starts. It pre-packs the most relevant files into a single markdown document so the agent's entire budget goes toward solving your problem — not browsing your codebase.

```
Without ctxpack:    [Agent reads 50 files one by one → budget exhausted → shallow analysis]
With ctxpack:       [ctxpack scores 500 files → packs top 12 → Agent gets 12 perfect files + structure]
```

### Workflow: ctxpack → Agent

```bash
# Step 1: Pack relevant context
ctxpack --path . --task "add rate limiting middleware" --budget 8000 --out context.md

# Step 2: Feed to your agent (tool-specific methods below)
```

### How to use ctxpack with each tool

| Tool | How to feed the bundle |
|------|----------------------|
| **Claude Code** | `claude --context context.md -p "add rate limiting based on this context"` |
| **OpenCode** | `opencode --context context.md` or paste bundle into the chat |
| **Codex CLI** | `codex --context context.md -p "implement the changes"` |
| **Copilot CLI** | Paste the bundle before your question: `gh copilot suggest "Based on this codebase, explain..."` |
| **Cursor** | Open `context.md` in a tab and reference `@context.md` in your prompt |
| **Windsurf** | Create a `context.md` file in `.windsurf/` for persistent context |
| **Any chat UI** | Copy the entire bundle and paste as the first message |

### Why the bundle format is agent-friendly

| Feature | Why it matters for agents |
|---------|-------------------------|
| **`## File:` headers** | Agent can parse and reference specific files |
| **Code fences** | Language-aware syntax — agent knows file type immediately |
| **`<!-- tokens: N -->`** | Agent can estimate remaining context budget |
| **Directory tree** | Agent understands project structure without `ls` |
| **Deterministic output** | Same context every time — cacheable, reproducible |
| **Sorted by relevance** | Most important files appear first — agent sees them first |

### Best practice: pre-context then iterate

```bash
# 1. Generate focused context
ctxpack --path ./src/api --task "add user authentication endpoints" --budget 4000 --out auth_context.md

# 2. Launch agent with context
claude --context auth_context.md -p "Implement the auth endpoints described. Read any additional files you need."

# 3. The agent will read more files if needed, but it starts with the essentials
#    already in its context — saving 60-80% of discovery tokens.
```

**Pro tip:** Run ctxpack from within the agent itself. Tell your agentic tool: *"Before you start, run ctxpack --path . --task '<what we are doing>' --budget 8000 --out ctx.md, then use ctx.md as your primary reference."* The bundle becomes a shared ground truth that keeps the agent focused.

---

## Quick Start

```bash
# Clone the repo
git clone https://github.com/Saleh-Mustufa/ctxpack.git
cd ctxpack

# Run on yourself (meta!) to understand how ctxpack works
python ctxpack.py --path . --task "understand the project structure" --budget 4000
```

That's it. No `pip install`, no `npm install`, no `requirements.txt`. Python 3.10+ is all you need.

---

## Requirements

| Requirement | Detail |
|-------------|--------|
| **Python** | 3.10 or higher |
| **Packages** | None — uses only Python standard library |
| **Internet** | Not required at runtime |
| **OS** | Windows, macOS, Linux |

---

## Installation

```bash
# Option 1: Clone the repo
git clone https://github.com/Saleh-Mustufa/ctxpack.git
cd ctxpack

# Option 2: Or just download the files
# curl -LO https://raw.githubusercontent.com/Saleh-Mustufa/ctxpack/main/ctxpack.py
# (you'll also need walker.py, ranker.py, bundler.py, formatter.py, manifest.py)

# No install step — just run:
python ctxpack.py --help
```

---

## Usage

```
python ctxpack.py --path <folder> --task "<description>" --budget <tokens> [options]
```

### Required Flags

| Flag | Type | Description |
|------|------|-------------|
| `--path` | string | Path to the folder you want to pack (the codebase root) |
| `--task` | string | What you're trying to do. Used to score file relevance. |
| `--budget` | integer | Maximum tokens for the entire bundle output |

### Optional Flags

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--out` | string | stdout | Write the bundle to a file instead of printing it |
| `--manifest` | string | (none) | Write a JSON manifest to a file accounting for every file |

---

## Examples

### 1. Basic — pack current folder, print to terminal

```bash
python ctxpack.py --path . --task "fix the login bug" --budget 8000
```

### 2. Save bundle to a file

```bash
python ctxpack.py --path ./src --task "add rate limiting" --budget 12000 --out bundle.md
```

### 3. Full workflow — bundle + manifest

```bash
python ctxpack.py \
  --path /path/to/project \
  --task "understand the database layer and API routes" \
  --budget 6000 \
  --out context.md \
  --manifest manifest.json
```

### 4. Small budget — pack just the key files

```bash
python ctxpack.py --path ./my_app --task "readme and entry point" --budget 1000
```

### 5. Code review preparation

```bash
python ctxpack.py --path ./pull-request-branch --task "review changes to payment processing" --budget 8000 --out review_bundle.md
```

### 6. Onboarding to a new project

```bash
python ctxpack.py --path ./legacy-monolith --task "understand the overall architecture and main entry points" --budget 16000 --out onboarding.md
```

### 7. Debugging — see what got excluded

```bash
python ctxpack.py --path . --task "refactor utils module" --budget 4000 --manifest debug.json
cat debug.json | python -m json.tool
```

### 8. Deterministic output (same hash every time)

```bash
SOURCE_DATE_EPOCH=1700000000 python ctxpack.py --path . --task "test" --budget 5000 | md5sum
```

---

## Sample Output

Here's what a bundle looks like:

```
# ctxpack bundle
# Task: understand the project structure
# Budget: 4000 tokens | Used: 3942 tokens
# Generated: 2026-07-27T13:42:23Z

## Project Structure

+-- ctxpack.py
+-- walker.py
+-- ranker.py
+-- bundler.py
+-- formatter.py
+-- manifest.py
+-- README.md
\-- SPEC.md

---

## File: ctxpack.py
<!-- tokens: 827 -->
```py
#!/usr/bin/env python3
...

```

---

## File: SPEC.md
<!-- tokens: 4188 -->
```md
# SPEC.md
...
```

```

The manifest (with `--manifest`) looks like:

```json
{
  "budget": 4000,
  "used": 3942,
  "included": [
    {"path": "ctxpack.py", "tokens": 827, "reason": "score=82.0, source-code"}
  ],
  "excluded": [
    {"path": "package-lock.json", "reason": "noise: lockfile"}
  ]
}
```

---

## Exit Codes

| Code | Meaning | When |
|------|---------|------|
| `0` | Success | Bundle was produced successfully |
| `1` | Invalid arguments | Missing a required flag, budget is not a positive integer |
| `2` | Path error | `--path` does not exist, is not a directory, or is unreadable |

All errors produce exactly one readable line to stderr. No raw Python tracebacks.

---

## How It Works

ctxpack has a 4-step pipeline:

### Step 1: Walker (`walker.py`)
Recursively walks the folder and discovers every file. Before scoring, it **filters noise** — files that can't contain useful signal:
- `.git/`, `__pycache__/`, `node_modules/`, `dist/`, `build/`
- Binary files (null bytes detected in first 8KB)
- Minified or generated files (heuristic detection)
- Lockfiles, bytecode, dependency trees

### Step 2: Ranker (`ranker.py`)
Scores each remaining file 0–100 using three signals:

| Signal | Weight | What it measures |
|--------|--------|-----------------|
| **Keyword overlap** | 60% | How many words from your task appear in the file's path + first 50 lines |
| **File priority** | 30% | Entry points (`main.py`) = 100, source code = 70, config = 40, data = 20 |
| **Depth penalty** | 10% | Files deeper than 4 folders lose 10 points per extra level |

Tie-break: alphabetical by path for determinism.

### Step 3: Bundler (`bundler.py` + `formatter.py`)
Sorts files by score (highest first), then greedily adds them until the budget is full. If a file doesn't fully fit:
- If it's ≤ 3× the remaining budget → include the **head** (first ~90% of remaining tokens) with a `[TRUNCATED]` marker
- If it's > 3× the remaining budget → exclude it with a reason

### Step 4: Manifest (`manifest.py`)
Produces a JSON file accounting for every file — included with token cost, excluded with the exact reason.

---

## Token Counting

The token rule is simple and deterministic:

```python
import math
def count_tokens(text: str) -> int:
    return math.ceil(len(text) / 4)
```

This counts **every character** in the bundle — headers, file paths, separators, code fences, directory tree, and file contents. Not just the code.

**Why this rule:** It's transparent, reproducible, and requires no external tokenizer. Every run produces the same count for the same input.

---

## Bundle Format

```
# ctxpack bundle
# Task: <description>
# Budget: <N> tokens | Used: <N> tokens
# Generated: <ISO 8601 UTC timestamp>

## Project Structure
<directory tree, max 300 tokens, only if budget ≥ 2000>

---

## File: <relative/path>
<!-- tokens: N -->
```<extension>
<file content>
```

---

## File: <relative/path>
<!-- tokens: N -->
```<extension>
<file content>
```

---
```

---

## Determinism

The **same command run twice on the same folder produces byte-identical output.**

What guarantees this:
- File ranking uses only path strings, extensions, and file content (read once)
- Tie-breaking is alphabetical — no hashing, no randomness, no modification times
- Token counting is a pure math function
- Greedy selection is fixed-order

**The one exception:** the `Generated:` timestamp changes each run. To make it deterministic:

```bash
export SOURCE_DATE_EPOCH=1700000000
python ctxpack.py --path . --task "test" --budget 5000 | md5sum
```

---

## Noise Filtering

Files excluded automatically before scoring:

| Pattern | Reason |
|---------|--------|
| `.git/`, `.hg/`, `.svn/` | Version control internals |
| `__pycache__/`, `*.pyc`, `*.pyo` | Python bytecode |
| `node_modules/`, `vendor/` | Dependency tree |
| `dist/`, `build/` | Build artifacts |
| `*.lock`, `package-lock.json` | Lockfiles |
| Binary files (null bytes) | Not text |
| Minified files (>50% lines >300 chars) | Generated code |
| Auto-generated files | No signal value |

---

## Tips & Best Practices

1. **Be specific in your task description.** "Fix the login form validation in auth.py" scores better than "fix a bug".

2. **Start with a moderate budget** (4000–8000 tokens) and increase if you need more files.

3. **Use `--manifest` to debug** what's being excluded and why.

4. **For very large projects**, run ctxpack on subdirectories rather than the root to avoid diluting the signal.

5. **Pair with `--out`** to save the bundle and paste it directly into your AI assistant.

6. **Budget guidelines:**
   - 1000 tokens → 1–2 small files
   - 4000 tokens → 5–10 files with brief headers
   - 8000 tokens → 10–20 files with directory tree
   - 16000 tokens → 20–40 files, good for understanding module-level architecture

---

## Project Structure

```
ctxpack/
├── ctxpack.py          # Thin CLI entry point (delegates to src/ctxpack.py)
├── src/                # Python implementation (stdlib only)
│   ├── ctxpack.py      #   CLI orchestration
│   ├── walker.py       #   File discovery + noise filtering
│   ├── ranker.py       #   Relevance scoring
│   ├── bundler.py      #   Token budget + greedy selection
│   ├── formatter.py    #   Bundle markdown + directory tree
│   └── manifest.py     #   JSON manifest output
├── tests/              # Test suite
│   └── test_edge_cases.py  # 16 edge case tests
├── docs/               # Documentation
│   ├── SPEC.md         #   Full specification document
│   ├── agent.md        #   AI context file
│   ├── PROMPTS.md      #   Development prompt journal
│   ├── JOURNAL.md      #   Design reflection
│   ├── WHAT_IS_CTXPACK.md  # 5W&H explanation
│   ├── USAGE_GUIDE.md   #   Beginner's tutorial
│   └── skill-ctxpack.md   #   Skill file for other AI agents
├── .opencode/          # OpenCode agent configuration
└── README.md           # This file
```

## AI Agent Skill

For other AI coding agents (Claude Code, OpenCode, Codex, etc.), a ready-to-use skill file is available at `docs/skill-ctxpack.md`. It teaches any agent how to use ctxpack autonomously:

```markdown
<!-- Tell your agent: "Read docs/skill-ctxpack.md for context packing instructions" -->
```

The skill covers: command syntax, bundle format parsing, scoring logic explained, noise rules, token counting, and common agent workflow templates.
