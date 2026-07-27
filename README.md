# ctxpack

Pack the most relevant files from any codebase into a single markdown context bundle that fits a token budget — designed for AI assistant context windows.

## Requirements

- Python 3.10+ (standard library only — no pip install needed)

## Quick Start

```bash
# Clone and run (no install step)
git clone <repo> && cd ctxpack
python ctxpack.py --path . --task "understand the project" --budget 8000
```

## Usage

```bash
python ctxpack.py --path <folder> --task "<description>" --budget <int> [--out <file>] [--manifest <file>]
```

### Example

```bash
# Pack the current project for a bug-fixing task
python ctxpack.py --path ./src --task "fix authentication bug" --budget 4000

# Write bundle to a file with manifest
python ctxpack.py --path . --task "add new feature" --budget 6000 --out bundle.md --manifest manifest.json
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Invalid arguments |
| 2 | Path not found or unreadable |

## How It Works

1. **Walker** — recursively discovers all files, filters noise (`.git/`, `__pycache__/`, `node_modules/`, binaries, lockfiles, etc.)
2. **Ranker** — scores each file 0–100 using keyword overlap (60%), file priority class (30%), and depth penalty (10%)
3. **Bundler** — greedily selects the highest-scoring files that fit the token budget; truncates oversized files
4. **Manifest** — produces a JSON manifest accounting for every file considered

## Token Counting

`tokens = math.ceil(len(text) / 4)` on the entire bundle output. No external tokenizers.

## Determinism

Same command + same folder → byte-identical output. Set `SOURCE_DATE_EPOCH` for deterministic timestamps.

## Project Structure

```
ctxpack/
├── ctxpack.py       # CLI entry point
├── walker.py        # File discovery + noise filtering
├── ranker.py        # Relevance scoring
├── bundler.py       # Token budget management + assembly
├── formatter.py     # Bundle markdown formatting
├── manifest.py      # JSON manifest output
├── test_edge_cases.py
├── SPEC.md          # Specification document
└── agent.md         # Context file
```
