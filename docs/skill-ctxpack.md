# Skill: ctxpack — Context Packer for Agentic AI

> Use this skill when an AI coding agent needs to prepare focused codebase context for itself or another agent.

## What ctxpack Is

A Python CLI (stdlib only, no install) that scans a folder, scores every file for relevance to a task, and packs the top files into one markdown bundle fitting a token budget.

```
ctxpack --path <folder> --task "<description>" --budget <tokens> [--out <file>] [--manifest <file>]
```

## When to Use This Skill

- Before launching an agentic coding tool (Claude Code, OpenCode, Codex)
- When context window is limited and you need the most relevant files
- To avoid wasting agent tokens on file discovery and directory browsing
- When you need deterministic, reproducible context bundles

## How Agents Should Use ctxpack

### Option A: Generate context, then consume

```bash
ctxpack --path . --task "<exact task description>" --budget 8000 --out ctx.md
```

Then feed `ctx.md` as initial context to the agent. The agent saves 60-80% of discovery tokens.

### Option B: Instruct the agent to run ctxpack itself

Add to the agent's instructions (CLAUDE.md, agent.md, or system prompt):

> Before reading any files, run `ctxpack --path . --task "<current_task>" --budget 8000 --out ctx.md`. Use ctx.md as your primary reference. Only read additional files if ctx.md lacks critical details.

## Bundle Format (agents can parse this)

```
# ctxpack bundle
# Task: <description>
# Budget: <N> tokens | Used: <N> tokens
# Generated: <ISO 8601 UTC>

## Project Structure
<directory tree>

---

## File: <relative/path>
<!-- tokens: N -->
```<ext>
<file content>
```

---
```

Key parsing cues for agents:
- `## File: <path>` — marks a new file boundary
- `<!-- tokens: N -->` — file content token cost, helps budget estimation
- `[TRUNCATED: showing X of Y tokens]` — file was cut at head due to budget
- Directory tree shows project shape

## How Scoring Works (so agents understand selection)

| Signal | Weight | What it measures |
|--------|--------|-----------------|
| Keyword overlap | 60% | Task words found in file path + first 50 lines |
| File priority | 30% | Entry points=100, source=70, config=40, data=20 |
| Depth penalty | 10% | Files >4 levels deep lose 10pts per extra level |

Files sorted by score descending. Tie-break: alphabetical path.

## What Gets Filtered (noise)

`.git/`, `__pycache__/`, `node_modules/`, `vendor/`, `dist/`, `build/`, `*.pyc`, `*.lock`, binaries (null bytes), minified files, auto-generated files.

## Token Rule

```python
tokens = math.ceil(len(text) / 4)  # on ENTIRE bundle
```

## Common Agent Workflows

### Pre-flight context for a coding task

```bash
ctxpack --path ./src --task "implement user authentication with JWT" --budget 6000 --out ctx.md
claude --context ctx.md -p "Implement the JWT auth following patterns in context"
```

### Debugging session

```bash
ctxpack --path . --task "fix the 500 error in payment processing" --budget 8000 --out bug.md
opencode --context bug.md
```

### Architecture exploration

```bash
ctxpack --path . --task "understand the database layer and API routing" --budget 12000 --out arch.md
# Then ask: "Based on this context, explain the architecture"
```

## Pro Tips for Agents

- **Be specific in `--task`** — "validate email format in user registration" beats "fix validation"
- **Budget sizing**: 4000 ≈ 5-10 files, 8000 ≈ 10-20, 16000 ≈ 20-40
- **Use `--manifest`** to see why files were excluded: `ctxpack ... --manifest manifest.json`
- **Deterministic output**: Set `SOURCE_DATE_EPOCH` env for byte-identical bundles
- **The bundle is ground truth** — if a file is in the bundle, the ranker deemed it relevant. Trust the selection; only read more files if something is missing.
