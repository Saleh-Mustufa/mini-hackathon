#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
import os


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="ctxpack",
        description="Pack the most relevant files from a codebase into a markdown context bundle.",

    )
    parser.add_argument("--path", help="Folder to pack")
    parser.add_argument("--task", help="Task description for relevance scoring")
    parser.add_argument("--budget", help="Maximum tokens for the bundle")
    parser.add_argument("--out", help="Write bundle to this file (default: stdout)")
    parser.add_argument("--manifest", help="Write manifest JSON to this file")
    return parser.parse_args(argv)


def validate_args(args: argparse.Namespace) -> None:
    if not args.path:
        print("Error: --path is required", file=sys.stderr)
        sys.exit(1)
    if not args.task:
        print("Error: --task is required", file=sys.stderr)
        sys.exit(1)
    if not args.budget:
        print("Error: --budget is required", file=sys.stderr)
        sys.exit(1)

    try:
        budget = int(args.budget)
    except ValueError:
        print("Error: --budget must be a positive integer", file=sys.stderr)
        sys.exit(1)

    if budget <= 0:
        print("Error: --budget must be a positive integer", file=sys.stderr)
        sys.exit(1)

    if not os.path.isdir(args.path):
        print(f"Error: path '{args.path}' not found or unreadable", file=sys.stderr)
        sys.exit(2)

    if args.out:
        out_dir = os.path.dirname(args.out)
        if out_dir and not os.path.isdir(out_dir):
            print(f"Error: output directory '{out_dir}' not found", file=sys.stderr)
            sys.exit(2)

    if args.manifest:
        manifest_dir = os.path.dirname(args.manifest)
        if manifest_dir and not os.path.isdir(manifest_dir):
            print(f"Error: manifest directory '{manifest_dir}' not found", file=sys.stderr)
            sys.exit(2)


def main(argv: list[str] | None = None) -> None:
    try:
        args = parse_args(argv)
        validate_args(args)

        budget = int(args.budget)

        from walker import walk_directory
        from ranker import rank_candidates
        from bundler import build_bundle
        from manifest import build_manifest, format_manifest, print_summary

        candidates, walker_excluded = walk_directory(args.path)

        scored = rank_candidates(candidates, args.task, args.path)

        result = build_bundle(scored, args.task, budget, args.path, walker_excluded)

        manifest = build_manifest(budget, result.used, result.included, result.excluded)

        if args.out:
            with open(args.out, 'w', encoding='utf-8') as f:
                f.write(result.bundle_str)
        else:
            sys.stdout.write(result.bundle_str)

        if args.manifest:
            with open(args.manifest, 'w', encoding='utf-8') as f:
                f.write(format_manifest(manifest))
        else:
            print_summary(len(result.included), len(result.excluded), result.used, budget)

    except SystemExit:
        raise
    except Exception as e:
        print(f"Error: unexpected error - {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
