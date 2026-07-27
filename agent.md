# ctxpack — agent.md

## Project
Python CLI tool: `ctxpack --path <folder> --task "<desc>" --budget <int> [--out <file>] [--manifest <file>]`
Packs the most relevant files from a codebase into a markdown context bundle that fits a token budget.

## Hard constraints
- Python 3.10+ standard library ONLY — no pip installs
- No network calls at runtime
- Token rule: `math.ceil(len(text) / 4)` on the ENTIRE output string
- Exit codes: 0 success, 1 bad args, 2 path not found
- Deterministic: same command → byte-identical output

## Architecture
- `ctxpack.py` — CLI entry point (argparse, exit codes, error handling)
- `walker.py` — recursive file discovery + noise filtering
- `ranker.py` — multi-signal relevance scoring
- `bundler.py` — token counting, budget management, truncation
- `manifest.py` — manifest schema + JSON output
- `formatter.py` — bundle markdown + directory tree

## Spec-first discipline
ALWAYS check SPEC.md before writing implementation. If a decision isn't in spec, add it to spec first, then implement.

## Graded deliverables (do not forget)
- SPEC.md (first commit, no code)
- agent.md (this file — context engineering artifact)
- PROMPTS.md (5 most important prompts with what changed and why)
- JOURNAL.md (5 questions, question 3 = what Claude got wrong)
- README.md (clone to first run in under 5 minutes)
