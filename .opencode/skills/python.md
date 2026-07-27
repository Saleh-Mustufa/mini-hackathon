# Python Skill

## Stdlib-Only Development
- Use only Python 3.10+ standard library modules
- No pip installs, no requirements.txt, no virtualenv needed
- Key modules: `argparse`, `os`, `pathlib`, `sys`, `json`, `math`, `unittest`, `datetime`, `enum`

## File I/O
- Use `pathlib.Path` for path manipulation over `os.path`
- For reading text files: `path.read_text(errors='ignore')` or `open(path, 'r', errors='ignore')`
- For binary detection: read first 8KB and check for null bytes (`b'\x00'`)
- Handle `PermissionError`, `FileNotFoundError`, `UnicodeDecodeError` gracefully

## Type Hints
- Use type hints for all function signatures (Python 3.10+)
- Use `|` for union types (Python 3.10+): `str | None` instead of `Optional[str]`
- Use `list[str]` instead of `List[str]`

## Exit Codes
- `sys.exit(0)` for success
- `sys.exit(1)` for argument errors
- `sys.exit(2)` for path/resource errors
