from __future__ import annotations

import json
import sys


def build_manifest(
    budget: int,
    used: int,
    included: list[dict],
    excluded: list[dict],
) -> dict:
    return {
        "budget": budget,
        "used": used,
        "included": included,
        "excluded": excluded,
    }


def format_manifest(manifest: dict) -> str:
    return json.dumps(manifest, indent=2)


def print_summary(included: int, excluded: int, used: int, budget: int) -> None:
    print(f"ctxpack: {included} files included, {excluded} excluded, {used}/{budget} tokens used", file=sys.stderr)
