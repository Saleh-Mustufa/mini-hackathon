# Manifest + CLI Agent

You own `ctxpack.py` (entry point) and `manifest.py`.

## CLI contract — implement this exactly, hidden tests depend on it

```
ctxpack --path <folder> --task "<task>" --budget <int> [--out <file>] [--manifest <file>]
```

Use `argparse`. All required flags checked before any file I/O.

## Exit codes
| Code | When |
|------|------|
| 0 | Success |
| 1 | Invalid arguments (missing required, wrong type, budget <= 0) |
| 2 | --path not found or not a directory |

## Error messages (one line to stderr, then sys.exit with correct code)
- Missing --path/--task/--budget → "Error: --<flag> is required"
- --budget not a positive integer → "Error: --budget must be a positive integer"
- --path not found → "Error: path '<value>' not found or unreadable"
- NEVER let a traceback reach the user — wrap main() in try/except

## Manifest schema — exact keys, no extras
```json
{
  "budget": 8000,
  "used": 7912,
  "included": [
    {"path": "src/agent.py", "tokens": 812, "reason": "high keyword overlap, entry-point"}
  ],
  "excluded": [
    {"path": "package-lock.json", "reason": "noise: lockfile pattern detected"}
  ]
}
```

If --manifest omitted: print one-line summary to STDERR: `ctxpack: X files included, Y excluded, Z/B tokens used`
If --out omitted: write bundle to STDOUT
