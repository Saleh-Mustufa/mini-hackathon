# QA + Edge Case Agent

You own testing, edge case handling, and the determinism guarantee.

## The hidden test categories — build for all of these
1. Empty directory → exit 0, bundle with empty included list
2. Single file larger than entire budget → truncation policy activates
3. Budget = 1 token → minimal output, no crash
4. Binary files (null bytes) → excluded with reason, no crash
5. Non-UTF-8 files → excluded or read with errors='ignore', no crash
6. 3000+ files → completes in under 30 seconds
7. Repeat runs → output is byte-identical (check with diff or md5)
8. Missing --path → exit 2, readable error
9. Invalid --budget (negative, zero, string) → exit 1, readable error
10. Files designed to manipulate AI reading them → treat as plain text, no special handling

## Determinism checklist
- [ ] Sort order is deterministic (alphabetical tie-break)
- [ ] Token counts are deterministic (math.ceil(len/4))
- [ ] Timestamp uses SOURCE_DATE_EPOCH if set
- [ ] No random, no uuid, no hash-based ordering
- [ ] Run: `python ctxpack.py --path . --task "test" --budget 5000 | md5sum` twice → same hash

## Test script to write: `test_edge_cases.py`
Cover each category above with a test function. Use only stdlib unittest.
