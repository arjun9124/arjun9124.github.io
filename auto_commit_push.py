#!/usr/bin/env python3
"""Commit and push all changes with an incrementing numeric commit title."""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
import subprocess
import sys


DEFAULT_COMMIT_TITLE = 11340507042043
LASTMOD_FILES = [
    Path("content/about.md"),
    Path("content/apni-rasoi.md"),
    Path("content/changelog.md"),
    Path("content/gumkosh.md"),
    Path("content/kaancept.md"),
    Path("content/mapsofdelhi-transit.md"),
    Path("content/mapsofdelhi-urban.md"),
    Path("content/meta.md"),
    Path("content/stick-mo-bills.md"),
    Path("content/teentaal.md"),
    Path("content/whats-going-on.md"),
]


def run(command: list[str]) -> subprocess.CompletedProcess[str]:
    print("+ " + " ".join(command))
    return subprocess.run(command, text=True, check=True)


def git_status_paths(paths: list[Path]) -> set[Path]:
    result = subprocess.run(
        ["git", "status", "--porcelain", "--", *(str(path) for path in paths)],
        text=True,
        capture_output=True,
        check=True,
    )

    changed_paths: set[Path] = set()
    for line in result.stdout.splitlines():
        path = line[3:]
        if " -> " in path:
            path = path.rsplit(" -> ", 1)[1]
        changed_paths.add(Path(path))

    return changed_paths


def read_text_preserving_bom(path: Path) -> tuple[str, bool]:
    raw = path.read_bytes()
    has_bom = raw.startswith(b"\xef\xbb\xbf")
    if has_bom:
        raw = raw[3:]
    return raw.decode("utf-8"), has_bom


def write_text_preserving_bom(path: Path, text: str, has_bom: bool) -> None:
    raw = text.encode("utf-8")
    if has_bom:
        raw = b"\xef\xbb\xbf" + raw
    path.write_bytes(raw)


def upsert_toml_front_matter_field(text: str, field: str, value: str) -> str:
    newline = "\r\n" if "\r\n" in text else "\n"
    lines = text.splitlines(keepends=False)

    if len(lines) < 2 or lines[0] != "+++":
        raise ValueError("expected TOML front matter delimited by +++")

    try:
        end_index = lines.index("+++", 1)
    except ValueError as error:
        raise ValueError("missing closing +++ front matter delimiter") from error

    replacement = f'{field} = "{value}"'
    for index in range(1, end_index):
        if lines[index].lstrip().startswith(f"{field} "):
            lines[index] = replacement
            return newline.join(lines) + (newline if text.endswith(("\n", "\r\n")) else "")

    insert_index = 1
    for index in range(1, end_index):
        if lines[index].lstrip().startswith("date "):
            insert_index = index + 1
            break
        if lines[index].lstrip().startswith("title "):
            insert_index = index + 1

    lines.insert(insert_index, replacement)
    return newline.join(lines) + (newline if text.endswith(("\n", "\r\n")) else "")


def update_lastmod_fields() -> None:
    existing_files = [path for path in LASTMOD_FILES if path.exists()]
    changed_paths = git_status_paths(existing_files)
    timestamp = datetime.now().astimezone().isoformat(timespec="seconds")

    for path in existing_files:
        text, has_bom = read_text_preserving_bom(path)
        has_lastmod = any(
            line.lstrip().startswith("lastmod ")
            for line in text.splitlines()
        )

        if path not in changed_paths and has_lastmod:
            continue

        updated_text = upsert_toml_front_matter_field(text, "lastmod", timestamp)
        if updated_text != text:
            write_text_preserving_bom(path, updated_text, has_bom)


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
        update_lastmod_fields()
        run(["git", "add", "-A"])
        run(["git", "commit", "-m", commit_title])
        run(["git", "push", "-u", args.remote, args.branch])
    except subprocess.CalledProcessError as error:
        return error.returncode

    return 0


if __name__ == "__main__":
    sys.exit(main())
