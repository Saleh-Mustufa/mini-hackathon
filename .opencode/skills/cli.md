# CLI Skill

## Argparse Best Practices
- Use `argparse.ArgumentParser` with `add_argument` for all flags
- Required flags use `required=True`
- Arguments with dashes in flag names use `--flag` convention
- Print errors to `sys.stderr`, never `sys.stdout`
- Exit with appropriate codes: 0 success, 1 args, 2 runtime

## Error Handling
```python
def main() -> None:
    try:
        args = parse_args()
        # ...
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
```

## Output Conventions
- Bundle output: stdout or file (controlled by `--out`)
- Error output: stderr
- Summary output: stderr
- Manifest output: file (controlled by `--manifest`)
