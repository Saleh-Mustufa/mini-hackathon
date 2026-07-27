# JOURNAL.md — Five Reflection Questions

## Question 1: What was the biggest technical challenge?

The biggest challenge was the bundle assembly loop — specifically managing the running token count while accounting for the formatting overhead (separators, headers, tree) around each file section. Each file section's token cost includes the `## File:` header, `<!-- tokens: N -->` comment, code fences, and the file content itself. The separator between files (`\n---\n\n`) adds additional tokens. Getting the greedy selection algorithm to correctly account for all overhead while respecting the budget required careful bookkeeping and two passes (one for selection, one for final assembly with accurate `used` count).

## Question 2: What would you do differently with more time?

1. **Tree formatting:** The ASCII directory tree is functional but ugly. With more time, I would implement Unicode box-drawing with proper parent tracking for cleaner output like the SPEC.md architecture section shows.
2. **Performance:** The 3000-file test takes ~30s. I would optimize the ranker to avoid reading file content twice (once for scoring, once for bundling).
3. **Regex-based scoring:** The keyword tokenizer uses a simple regex split. A proper tokenizer would handle compound identifiers (`snake_case`, `CamelCase`) better.
4. **Parallel file reads:** Walker and ranker could use concurrent.futures for parallel file I/O on large repos.

## Question 3: What did Claude (AI assistant) get wrong?

Claude (the model) got several things wrong during development:

1. **Truncation threshold:** The bundler-agent.md was given with `floor(R × 0.95)` but SPEC.md §6 clearly states `floor(R × 0.90)`. Claude didn't cross-reference the agent prompt against the spec — it had to be pointed out.

2. **Tree characters:** Claude initially used Unicode box-drawing characters (├── └── │) which caused `'charmap' codec can't encode character` errors on Windows. The fix was to switch to ASCII-only characters (+--, \\--, |).

3. **Argparse exit codes:** Claude used `required=True` on argparse flags, which causes argparse to exit with code 2 on missing arguments. But SPEC.md requires exit code 1 for bad arguments. This had to be fixed by removing `required=True` and doing manual validation.

4. **Token display:** The `<!-- tokens: N -->` showed 0 for all files initially because the placeholder wasn't updated with the actual computed token count.

## Question 4: What was the most surprising edge case?

The Windows `'charmap' codec can't encode character` error was surprising. The bundle generated correctly (all text, no binary), but `sys.stdout.write()` on Windows uses the system locale encoding (cp1252) by default, which can't encode the Unicode tree characters. This is a runtime environment issue, not a logic bug, but it means the tool would crash on `sys.stdout.write()` for any bundle containing characters outside the current code page. The fix was to use ASCII-only characters throughout the output, which also improves portability.

## Question 5: What is the weakest part of the current implementation?

The **keyword scoring in ranker.py** is the weakest component. It tokenizes the task description by splitting on `[a-zA-Z0-9_]+` and counts matches in the file path + first 50 content lines. This is fast and deterministic, but:
- It doesn't handle synonyms ("fix" ≠ "bug", "test" ≠ "unittest")
- Short task descriptions (1-2 words) produce very few tokens, making the keyword signal noisy
- Long task descriptions get more signal but the equality check is strict (no stemming, no fuzzy matching)
- The 50-line content peek may miss relevant code in files with long imports/docstrings before the actual logic

A better approach would use TF-IDF-like scoring with substring matching, but that would require reading all file contents upfront, which conflicts with the performance requirement for 3000+ files.
