#!/usr/bin/env python3
"""Commit and push all changes with an incrementing numeric commit title."""

from __future__ import annotations

import argparse
import subprocess
import sys


DEFAULT_COMMIT_TITLE = 11340507042043


def run(command: list[str]) -> subprocess.CompletedProcess[str]:
    print("+ " + " ".join(command))
    return subprocess.run(command, text=True, check=True)


def latest_commit_title() -> str | None:
    result = subprocess.run(
        ["git", "log", "-1", "--pretty=%s"],
        text=True,
        capture_output=True,
    )

    if result.returncode != 0:
        return None

    title = result.stdout.strip()
    return title or None


def next_commit_title(start: int) -> str:
    title = latest_commit_title()

    if title and title.isdigit():
        return str(int(title) + 1)

    return str(start + 1)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run git add -A, commit with a +1 numeric title, then push main."
    )
    parser.add_argument(
        "--start",
        type=int,
        default=DEFAULT_COMMIT_TITLE,
        help=f"Fallback value to increment if the latest commit title is not numeric. Default: {DEFAULT_COMMIT_TITLE}",
    )
    parser.add_argument(
        "--remote",
        default="origin",
        help="Git remote to push to. Default: origin",
    )
    parser.add_argument(
        "--branch",
        default="main",
        help="Git branch to push. Default: main",
    )
    args = parser.parse_args()

    commit_title = next_commit_title(args.start)

    try:
        run(["git", "add", "-A"])
        run(["git", "commit", "-m", commit_title])
        run(["git", "push", "-u", args.remote, args.branch])
    except subprocess.CalledProcessError as error:
        return error.returncode

    return 0


if __name__ == "__main__":
    sys.exit(main())
