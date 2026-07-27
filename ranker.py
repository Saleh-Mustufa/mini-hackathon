from __future__ import annotations

import math
import os
import re
from pathlib import Path
from typing import NamedTuple

from walker import FileCandidate


class ScoredFile(NamedTuple):
    path: str
    score: float
    priority_class: str


ENTRY_POINT_NAMES = {'main.py', '__main__.py', '__init__.py'}
ENTRY_POINT_STEMS = {'index', 'app', 'server'}
SOURCE_EXTENSIONS = {'.py', '.js', '.ts', '.go', '.rs', '.java', '.c', '.cpp'}
CONFIG_EXTENSIONS = {'.json', '.toml', '.yaml', '.yml', '.ini', '.cfg'}
SPEC_EXTENSIONS = {'.md', '.rst', '.txt'}


def _get_priority(path: str, extension: str) -> tuple[int, str]:
    fname = Path(path).name
    stem = Path(path).stem

    if fname in ENTRY_POINT_NAMES or stem in ENTRY_POINT_STEMS:
        return 100, "entry-point"
    if extension in SPEC_EXTENSIONS and not extension == '.lock':
        return 90, "spec-doc"
    if extension in SOURCE_EXTENSIONS:
        return 70, "source-code"
    if extension in CONFIG_EXTENSIONS:
        return 40, "config"
    return 20, "data-text"


def _tokenize(text: str) -> set[str]:
    tokens = re.findall(r'[a-zA-Z0-9_]+', text.lower())
    return set(tokens)


def _compute_keyword_score(path: str, extension: str, root_path_str: str, task_tokens: set[str]) -> float:
    if not task_tokens:
        return 0.0

    path_tokens = _tokenize(path)
    matches = len(path_tokens & task_tokens)

    content_matches = 0
    abs_path = os.path.join(root_path_str, path)
    try:
        with open(abs_path, 'r', errors='ignore') as f:
            content_lines = []
            for _ in range(50):
                try:
                    line = f.readline()
                except Exception:
                    break
                if not line:
                    break
                content_lines.append(line)
        content_text = ' '.join(content_lines)
        content_tokens = _tokenize(content_text)
        content_matches = len(content_tokens & task_tokens)
    except Exception:
        pass

    total_tokens = len(task_tokens)
    if total_tokens == 0:
        return 0.0
    score = (matches + content_matches) / total_tokens
    return min(score, 1.0)


def _compute_depth_score(depth: int) -> float:
    if depth <= 4:
        return 1.0
    penalty = (depth - 4) * 10
    return max(0.0, 100.0 - penalty) / 100.0


def rank_candidates(
    candidates: list[FileCandidate],
    task: str,
    root_path: str,
) -> list[ScoredFile]:
    task_tokens = _tokenize(task)

    scored: list[ScoredFile] = []
    for c in candidates:
        priority_score, priority_class = _get_priority(c.path, c.extension)
        keyword_score = _compute_keyword_score(c.path, c.extension, root_path, task_tokens)
        depth_score = _compute_depth_score(c.depth)

        final_score = (keyword_score * 60.0) + ((priority_score / 100.0) * 30.0) + (depth_score * 10.0)

        scored.append(ScoredFile(path=c.path, score=round(final_score, 2), priority_class=priority_class))

    scored.sort(key=lambda s: (-s.score, s.path))
    return scored
