# WHAT IS CTXPACK? — 5W&H

## What is it?

**ctxpack** (Context Packer) is a Python CLI tool that takes a folder of code, reads your task description, and automatically selects the most relevant files to pack into a single markdown document that fits within a token budget.

Think of it as a smart "copy-paste" for AI assistants. Instead of manually hunting down which files to include in your AI prompt, ctxpack does the selection for you — intelligently, deterministically, and within your context window limit.

## Why does it exist?

**The context window problem:** AI coding assistants (Claude, GPT, Copilot, etc.) have limited context windows — typically 8K to 200K tokens. A medium-sized project has thousands of files totaling millions of tokens. You cannot paste everything.

You *could* manually select files, but:
- You might miss something important
- You might include irrelevant noise
- It takes time and judgment
- Different tasks need different files from the same project

ctxpack solves this by **automatically scoring and selecting** the most relevant files for your specific task.

## When should you use it?

| Scenario | Why ctxpack helps |
|----------|-------------------|
| **Before an AI prompt** | You're about to ask Claude/GPT to write code, fix a bug, or explain something. Pack the relevant files and paste the bundle as context. |
| **Code review** | You need to review a change and want to understand the surrounding code. Pack the relevant area. |
| **Onboarding to a new project** | You just joined a team and need to understand the codebase. Pack the architecture and core files. |
| **Debugging** | You're tracking down a bug and want the AI to see related files. Describe the bug as the task. |
| **Documentation generation** | You want an AI to write docs for specific modules. Pack those modules with context. |
| **Refactoring planning** | You're planning a refactor and want the AI to understand the current structure. |

Don't use ctxpack for:
- Running code or executing commands (it only produces text)
- Analyzing binary or non-text files (those are filtered out)
- Projects where you *can* paste everything (just use your editor's copy)

## Where does it work?

**Anywhere Python 3.10+ runs.** No installation, no dependencies, no internet needed.

- **Local development** — any folder on your machine
- **CI/CD pipelines** — generate context bundles during builds
- **Containers** — Docker, dev containers
- **Remote servers** — over SSH
- **Any OS** — Windows, macOS, Linux

It works on any text-file codebase: Python, JavaScript, TypeScript, Go, Rust, Java, C, C++, Ruby, PHP, shell scripts, config files, documentation — anything with readable text files.

## Who is it for?

- **Software engineers** using AI coding assistants
- **Technical leads** reviewing code and onboarding new team members
- **Open source maintainers** triaging issues and reviewing PRs
- **Students** learning codebases and asking AI for explanations
- **Anyone** who needs to give an AI relevant code context quickly

## How does it work?

ctxpack operates in 4 steps — no magic, all transparent:

```
                 +-----------+
                 | Your Code |
                 |  Folder   |
                 +-----+-----+
                       |
                       v
              +--------+--------+
         +--->    Walker.py     <---+
         |    +--------+--------+    |
         |            |              |
         |            v              |
         |    +--------+--------+   |  Noise filtered out:
    Files     |    Ranker.py     |   |  .git, node_modules,
    +         +--------+--------+   |  binaries, lockfiles,
    |                  |            |  minified code...
    |                  v            |
    |    +--------+--------+        |
    +--->    Bundler.py     |        |
         +--------+--------+        |
                  |                 |
                  v                  |
         +--------+--------+        |
         |  Manifest.py     |        |
         +--------+---------+       |
                  |                  |
          +-------+------+           |
          |              |           |
          v              v           |
    Bundle .md     manifest.json     |
    (paste this     (audit trail)    |
     into AI)           ^            |
                        +------------+
```

1. **Walker** — walks every file in your folder, filters out noise (`.git/`, `node_modules/`, binaries, lockfiles, etc.)
2. **Ranker** — scores each remaining file 0–100 by matching your task description against the file path and content
3. **Bundler** — picks the highest-scoring files that fit in your token budget, truncating oversized files at the head
4. **Manifest** — creates a JSON record of every file: included with token cost, excluded with reason

**The ranking formula (transparent and deterministic):**
- 60% — How many task keywords appear in the file path and first 50 lines
- 30% — File type priority (entry points > source code > config > data)
- 10% — Depth bonus (files in shallow directories score higher)

**The token rule:**
```python
tokens = math.ceil(len(text) / 4)
```
Applied to the *entire* bundle — every character, every header, every separator.

**Key properties:**
- ✅ **Deterministic** — same input always gives same output
- ✅ **Fast** — handles 3000+ files in under 30 seconds
- ✅ **Zero dependencies** — Python stdlib only
- ✅ **Transparent** — you can see exactly why each file was included or excluded
