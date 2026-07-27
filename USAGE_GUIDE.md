# USAGE GUIDE — ctxpack for Complete Beginners

This guide assumes you have **never used a command-line tool before**. We'll go step by step.

---

## Table of Contents

1. [What You Need](#1-what-you-need)
2. [Open a Terminal](#2-open-a-terminal)
3. [Find ctxpack on Your Computer](#3-find-ctxpack-on-your-computer)
4. [Your First Command](#4-your-first-command)
5. [Understanding the Output](#5-understanding-the-output)
6. [Three Complete Walkthroughs](#6-three-complete-walkthroughs)
   - [Walkthrough A: Understand an Unknown Project](#walkthrough-a-understand-an-unknown-project)
   - [Walkthrough B: Debug a Bug](#walkthrough-b-debug-a-bug)
   - [Walkthrough C: Code Review Prep](#walkthrough-c-code-review-prep)
7. [Common Mistakes & Fixes](#7-common-mistakes--fixes)
8. [Template Cheat Sheet](#8-template-cheat-sheet)

---

## 1. What You Need

- **Python 3.10 or higher** installed on your computer
- The ctxpack files (download the project)
- A code folder you want to analyze

**How to check if Python is installed:**

Open a terminal (see step 2 below) and type:

```
python --version
```

If you see `Python 3.10.x` or higher, you're good. If you get an error, download Python from [python.org](https://python.org).

> **Windows users:** If `python` doesn't work, try `py` or `python3`.

---

## 2. Open a Terminal

**Windows:**
- Press `Windows Key + R`, type `cmd`, press Enter
- OR search for "Command Prompt" or "PowerShell" in the Start menu

**macOS:**
- Press `Cmd + Space`, type `Terminal`, press Enter

**Linux:**
- Press `Ctrl + Alt + T`

This is where you'll type commands. You should see a blinking cursor and something like:

```
C:\Users\YourName>
```

or

```
yourname@computer:~$
```

---

## 3. Find ctxpack on Your Computer

You need to tell the terminal where ctxpack's files are. Use the `cd` command (change directory):

```bash
# Navigate to where you downloaded ctxpack
# Example: if it's on your Desktop named "ctxpack"
cd Desktop/ctxpack
```

**On Windows:**
```cmd
cd C:\Users\YourName\Desktop\ctxpack
```

**Verify you're in the right place:**

```bash
# List files — you should see ctxpack.py among them
ls
```

If you see `ctxpack.py` in the output, you're in the right place.

---

## 4. Your First Command

Let's run ctxpack on itself to see how it works:

```bash
python ctxpack.py --path . --task "understand how this tool works" --budget 4000
```

Let's break down this command:

| Part | Meaning |
|------|---------|
| `python` | Run this using Python |
| `ctxpack.py` | The ctxpack program |
| `--path .` | Look at the **current folder** (the `.` means "here") |
| `--task "..."` | I want to **understand how this tool works** |
| `--budget 4000` | Use at most **4000 tokens** (about 16,000 characters) |

Press Enter. You'll see output like:

```
ctxpack: 8 files included, 15 excluded, 3942/4000 tokens used
```

Then a markdown bundle will be printed to your terminal. That's the context pack!

> **Tip:** If you see a lot of text fly by, try saving to a file instead (see Walkthrough A).

---

## 5. Understanding the Output

The output has two parts:

### Part A: The Summary (printed to stderr)

```
ctxpack: 8 files included, 15 excluded, 3942/4000 tokens used
```

This tells you:
- **8 files included** — these are in your bundle
- **15 excluded** — these were skipped (noise, too large, etc.)
- **3942/4000 tokens used** — you're under budget

### Part B: The Bundle (printed to stdout or saved to a file)

The bundle looks like this:

```
# ctxpack bundle
# Task: understand how this tool works
# Budget: 4000 tokens | Used: 3942 tokens
# Generated: 2026-07-27T13:42:23Z

## Project Structure
... (directory tree) ...

---

## File: ctxpack.py
<!-- tokens: 827 -->
```py
... (file contents) ...
```
```

You can copy this entire bundle and paste it into an AI chat as context.

---

## 6. Three Complete Walkthroughs

### Walkthrough A: Understand an Unknown Project

**Scenario:** You just joined a team and need to understand a new codebase.

**Step 1:** Navigate to the project folder

```bash
cd path/to/the/project
```

**Step 2:** Run ctxpack with a broad task and large budget

```bash
python ctxpack.py --path . --task "understand the overall architecture, main entry points, and how modules connect" --budget 16000 --out context.md --manifest manifest.json
```

This creates two files:
- `context.md` — the bundle you can paste into AI
- `manifest.json` — details on every file

**Step 3:** Check the manifest to understand what was selected

```bash
# On macOS/Linux:
cat manifest.json

# On Windows:
type manifest.json
```

**Step 4:** Paste `context.md` into your AI assistant and ask:
> "I'm new to this project. Based on this context, explain the architecture and how to get started."

---

### Walkthrough B: Debug a Bug

**Scenario:** Users report that login fails with "invalid token" error. You want the AI to help find the bug.

**Step 1:** Run ctxpack with a focused task

```bash
python ctxpack.py --path ./src --task "debug login authentication token validation" --budget 8000 --out bug_context.md
```

**Step 2:** Paste the bundle into AI with a prompt like:
> "Here's my codebase context. The login is failing with 'invalid token' error. Find the bug and suggest a fix."

**Step 3:** ctxpack automatically selected auth-related files because the task mentioned "login", "authentication", and "token". If something is missing, increase the budget or narrow the path.

---

### Walkthrough C: Code Review Prep

**Scenario:** A teammate opened a pull request changing the payment API. You need to review it.

**Step 1:** Switch to the PR branch and run ctxpack

```bash
git checkout feature/new-payment-api

python ctxpack.py \
  --path . \
  --task "review the new payment API implementation" \
  --budget 10000 \
  --out review_context.md \
  --manifest review_manifest.json
```

**Step 2:** Examine the manifest to see if relevant files were included

```bash
python -c "import json; d=json.load(open('review_manifest.json')); [print(i['path'], '->', i['reason']) for i in d['included']]"
```

**Step 3:** Paste `review_context.md` into AI and ask:
> "Review this code for security issues, error handling, and test coverage."

---

## 7. Common Mistakes & Fixes

### Mistake 1: "python is not recognized"

**Fix:** Python isn't installed or not in your PATH.
- Install Python from [python.org](https://python.org)
- Or try: `py`, `python3`, `py -3`

### Mistake 2: "Error: --path is required"

**Fix:** You forgot to add `--path` to your command.
```bash
# Wrong:
python ctxpack.py --task "fix bug" --budget 5000

# Correct:
python ctxpack.py --path . --task "fix bug" --budget 5000
```

### Mistake 3: "Error: --budget must be a positive integer"

**Fix:** Budget must be a whole number greater than 0.
```bash
# Wrong:
python ctxpack.py --path . --task "fix" --budget 8k
python ctxpack.py --path . --task "fix" --budget 8000.5
python ctxpack.py --path . --task "fix" --budget -500

# Correct:
python ctxpack.py --path . --task "fix" --budget 8000
```

### Mistake 4: Bundle is way too long / over budget

**Fix:** Pick a smaller subfolder and reduce the budget.
```bash
# Instead of the whole project:
python ctxpack.py --path ./src/auth --task "fix authentication" --budget 4000
```

### Mistake 5: Output shows "0 files included"

**Fix:** Your budget might be too small for even the headers, or all files were filtered as noise.
```bash
# Try a larger budget:
python ctxpack.py --path . --task "anything" --budget 4000
```

### Mistake 6: I don't understand the manifest

The manifest has four sections:
- `budget` — the budget you set
- `used` — tokens actually used
- `included` — files in the bundle (with path, tokens, and reason)
- `excluded` — files skipped (with path and reason)

Each excluded file has a clear reason:
- `"noise: ..."` — the file was filtered during walk phase
- `"too large: ..."` — the file was too big for remaining budget
- `"budget exhausted"` — ran out of tokens

---

## 8. Template Cheat Sheet

Copy and paste these, just change the values in `[brackets]`:

### Explore a project
```bash
python ctxpack.py --path [folder] --task "explain the architecture" --budget 8000
```

### Fix a bug
```bash
python ctxpack.py --path [folder] --task "debug [describe the bug]" --budget 6000 --out bug.md
```

### Add a feature
```bash
python ctxpack.py --path [folder] --task "implement [feature description]" --budget 12000 --out feature_context.md --manifest manifest.json
```

### Code review
```bash
python ctxpack.py --path [folder] --task "review [what changed]" --budget 10000 --out review.md
```

### Write documentation
```bash
python ctxpack.py --path [folder] --task "document the [module name] module" --budget 8000 --out doc_context.md
```

### Quick peek (minimal budget)
```bash
python ctxpack.py --path [folder] --task "list the key files" --budget 500
```

### Full audit (with manifest)
```bash
python ctxpack.py --path [folder] --task "complete codebase understanding" --budget 32000 --out full.md --manifest full.json
```

### Deterministic output (same hash every run)
```bash
SOURCE_DATE_EPOCH=1700000000 python ctxpack.py --path [folder] --task "test" --budget 5000 | md5sum
```
