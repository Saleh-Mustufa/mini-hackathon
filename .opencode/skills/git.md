# Git Skill

## Commit Discipline
- First commit: ONLY SPEC.md (no implementation code)
- Each module gets its own commit after completion
- Never commit broken code
- Use conventional commit messages: `module: description`
- Verify commits: `git show --stat HEAD`

## Workflow
```bash
git add <files>
git commit -m "module: description"
git push
```

## Key Commands
- `git status` — check staged/unstaged changes
- `git diff` — review changes before commit
- `git log --oneline` — review commit history
- `git show --stat HEAD` — verify latest commit contents
- `git reset HEAD -- <file>` — unstage a file
