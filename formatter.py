from __future__ import annotations

import math
from datetime import datetime, timezone
from pathlib import Path


def count_tokens(text: str) -> int:
    return math.ceil(len(text) / 4)


def format_bundle_header(task: str, budget: int, used: int, timestamp: str | None = None) -> str:
    if timestamp is None:
        timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    lines = [
        f"# ctxpack bundle",
        f"# Task: {task}",
        f"# Budget: {budget} tokens | Used: {used} tokens",
        f"# Generated: {timestamp}",
        "",
    ]
    return "\n".join(lines)


def format_tree(file_paths: list[str], max_tokens: int) -> str:
    if max_tokens <= 0:
        return ""

    sorted_paths = sorted(file_paths)
    tree_lines: list[str] = ["## Project Structure", ""]

    if not sorted_paths:
        tree_lines.append("(empty directory)")
        return "\n".join(tree_lines)

    prefix_is_dir: dict[str, bool] = {}
    for p in sorted_paths:
        parts = p.replace('\\', '/').split('/')
        for i in range(len(parts)):
            prefix = '/'.join(parts[:i + 1])
            prefix_is_dir[prefix] = (i < len(parts) - 1)

    sorted_prefixes = sorted(prefix_is_dir.keys(), key=lambda k: (k.count('/'), k))
    by_depth: dict[int, list[str]] = {}
    for pref in sorted_prefixes:
        d = pref.count('/')
        by_depth.setdefault(d, []).append(pref)

    for depth in sorted(by_depth.keys()):
        items = by_depth[depth]
        for i, pref in enumerate(items):
            name = pref.split('/')[-1]
            if prefix_is_dir[pref]:
                name += '/'
            is_last = (i == len(items) - 1)

            connector = "+-- "
            indent = ""
            if depth > 0:
                parent = '/'.join(pref.split('/')[:-1])
                parent_items = by_depth.get(depth - 1, [])
                parent_is_last = (parent_items.index(parent) == len(parent_items) - 1) if parent in parent_items else True

                if depth > 1:
                    for d in range(1, depth):
                        ancestor = '/'.join(pref.split('/')[:d + 1])
                        items_at_d = by_depth.get(d, [])
                        last_prefix = items_at_d[-1] if items_at_d else ""
                        ancestor_last = (ancestor.split('/')[d] == last_prefix.split('/')[d]) if len(last_prefix.split('/')) > d else True
                        if ancestor_last:
                            indent += "    "
                        else:
                            indent += "|   "

                if is_last:
                    connector = "\\-- "
                else:
                    connector = "+-- "
            else:
                connector = "+-- "

            tree_lines.append(indent + connector + name)

    tree_str = "\n".join(tree_lines)
    tree_tok = count_tokens(tree_str)
    if tree_tok > max_tokens:
        while tree_lines and count_tokens("\n".join(tree_lines)) > max_tokens:
            tree_lines.pop()
        if tree_lines and tree_lines[-1] != "...(tree truncated)":
            tree_lines.append("...(tree truncated)")
        tree_str = "\n".join(tree_lines)

    return tree_str


def format_file_section(relative_path: str, content: str, content_tokens: int) -> str:
    ext = Path(relative_path).suffix.lstrip('.')
    lines = [
        f"## File: {relative_path}",
        f"<!-- tokens: {content_tokens} -->",
        f"```{ext}",
        content,
        "```",
    ]
    return "\n".join(lines)
