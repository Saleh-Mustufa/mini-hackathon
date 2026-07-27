from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path
from typing import NamedTuple

from formatter import (
    count_tokens,
    format_bundle_header,
    format_file_section,
    format_tree,
)
from ranker import ScoredFile


class BundleResult(NamedTuple):
    bundle_str: str
    used: int
    included: list[dict]
    excluded: list[dict]


def _get_timestamp() -> str:
    epoch = os.environ.get('SOURCE_DATE_EPOCH')
    if epoch is not None:
        try:
            return datetime.fromtimestamp(int(epoch), tz=timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
        except (ValueError, OSError):
            pass
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def _section_separator() -> str:
    return "\n---\n\n"


def build_bundle(
    scored_files: list[ScoredFile],
    task: str,
    budget: int,
    root_path: str,
    walker_excluded: list[dict],
) -> BundleResult:
    included: list[dict] = []
    excluded: list[dict] = list(walker_excluded)

    ts = _get_timestamp()
    header = format_bundle_header(task, budget, 0, ts)
    header_tokens = count_tokens(header)

    tree_str = ""
    tree_tokens = 0
    if budget >= 2000:
        all_paths = sorted(sf.path for sf in scored_files)
        tree_str = format_tree(all_paths, 300)
        tree_tokens = count_tokens(tree_str)

    total_header_overhead = header_tokens + tree_tokens
    remaining = budget - total_header_overhead

    scored_sorted = sorted(scored_files, key=lambda s: (-s.score, s.path))
    sections: list[str] = []
    is_first = True

    for sf in scored_sorted:
        prelim_header = f"## File: {sf.path}\n<!-- tokens: 0 -->\n```\n```"
        prelim_tokens = count_tokens(prelim_header)
        sep_tokens = 0 if is_first else count_tokens(_section_separator())

        if remaining <= sep_tokens + prelim_tokens:
            excluded.append({
                "path": sf.path,
                "reason": f"budget exhausted: {remaining} tokens remaining"
            })
            continue

        abs_path = os.path.join(root_path, sf.path)
        file_content = ""
        try:
            file_content = Path(abs_path).read_text(errors='ignore')
        except Exception as e:
            excluded.append({
                "path": sf.path,
                "reason": f"unreadable: {type(e).__name__}"
            })
            continue

        content_tokens = count_tokens(file_content)
        section = format_file_section(sf.path, file_content, content_tokens)
        section_tokens = count_tokens(section)

        cost = (0 if is_first else count_tokens(_section_separator())) + section_tokens

        if cost <= remaining:
            included.append({
                "path": sf.path,
                "tokens": content_tokens,
                "reason": f"score={sf.score}, {sf.priority_class}"
            })
            sections.append(section)
            remaining -= cost
            is_first = False
        elif section_tokens <= 3 * remaining:
            max_content_chars = int(remaining * 0.90 * 4)
            truncated_content = file_content[:max_content_chars]
            truncated_actual_tokens = count_tokens(truncated_content)
            trunc_note = f"\n[TRUNCATED: showing {truncated_actual_tokens} of {content_tokens} tokens]"
            truncated_content += trunc_note
            truncated_section = format_file_section(sf.path, truncated_content, truncated_actual_tokens)
            truncated_cost = (0 if is_first else count_tokens(_section_separator())) + count_tokens(truncated_section)
            if truncated_cost <= remaining:
                included.append({
                    "path": sf.path,
                    "tokens": truncated_actual_tokens,
                    "reason": f"truncated: score={sf.score}, {sf.priority_class}"
                })
                sections.append(truncated_section)
                remaining -= truncated_cost
                is_first = False
            else:
                excluded.append({
                    "path": sf.path,
                    "reason": f"too large: {content_tokens} tokens, only {remaining} remaining"
                })
        else:
            excluded.append({
                "path": sf.path,
                "reason": f"too large: {content_tokens} tokens, only {remaining} remaining"
            })

    ts = _get_timestamp()
    header = format_bundle_header(task, budget, 0, ts)

    sep = _section_separator()
    body = sep.join(sections)
    bundle_parts = [header]
    if tree_str:
        bundle_parts.append(tree_str)
    if body:
        bundle_parts.append(body)

    full_bundle = "\n\n".join(bundle_parts)
    actual_used = count_tokens(full_bundle)

    header = format_bundle_header(task, budget, actual_used, ts)
    bundle_parts[0] = header
    full_bundle = "\n\n".join(bundle_parts)
    actual_used = count_tokens(full_bundle)

    if actual_used > budget and sections:
        while sections and count_tokens("\n\n".join([header] + ([tree_str] if tree_str else []) + [sep.join(sections)])) > budget:
            removed = sections.pop()
            last_entry = included.pop()
            excluded.append({
                "path": last_entry["path"],
                "reason": f"dropped during budget enforcement: {last_entry['tokens']} tokens"
            })
            body = sep.join(sections)
            bundle_parts = [header]
            if tree_str:
                bundle_parts.append(tree_str)
            if body:
                bundle_parts.append(body)
            full_bundle = "\n\n".join(bundle_parts)
            actual_used = count_tokens(full_bundle)
            header = format_bundle_header(task, budget, actual_used, ts)
            bundle_parts[0] = header
            full_bundle = "\n\n".join(bundle_parts)
            actual_used = count_tokens(full_bundle)

    if not sections and actual_used > budget:
        header = format_bundle_header(task, budget, actual_used, ts)
        bundle_parts[0] = header
        full_bundle = "\n\n".join(bundle_parts)
        actual_used = count_tokens(full_bundle)

    return BundleResult(
        bundle_str=full_bundle,
        used=actual_used,
        included=included,
        excluded=excluded,
    )
