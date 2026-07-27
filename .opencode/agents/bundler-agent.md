# Bundler Agent

You own `bundler.py` and `formatter.py`.

## Token counting — this is the law
```python
import math
def count_tokens(text: str) -> int:
    return math.ceil(len(text) / 4)
```
This applies to the ENTIRE bundle string — every character of headers, separators, paths, tree, content.

## Budget algorithm
1. Sort candidates by score descending
2. Reserve tokens for the bundle header (~100 tokens) and directory tree (if budget >= 2000, reserve up to 300 tokens)
3. Greedily add files from ranked list until budget is exhausted
4. For each file that doesn't fit:
   - If file_tokens <= 3 * remaining: include HEAD, truncate at floor(remaining * 0.90) tokens, append `\n[TRUNCATED: showing X of Y tokens]`
   - If file_tokens > 3 * remaining: exclude entirely, manifest reason = "too large: X tokens, Y remaining"

## Bundle format (exact)
# ctxpack bundle
# Task: <task>
# Budget: <N> tokens | Used: <N> tokens
# Generated: <ISO 8601 UTC>

## Project Structure
<tree — max 300 tokens, only if budget >= 2000>

---
## File: <relative/path>
<!-- tokens: N -->
```<extension>
<content>
```

## Determinism
- Never use random, uuid, or wall-clock time for anything affecting content
- Timestamp in header uses UTC: `datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')`
- If `SOURCE_DATE_EPOCH` env var is set, use it instead of current time
