#!/usr/bin/env python3
"""Commit and push all changes with an incrementing numeric commit title."""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
import subprocess
import sys


DEFAULT_COMMIT_TITLE = 11340507042043
CONTENT_DIR = Path("content")
CONTENT_FILE_GLOB = "*.md"


def run(command: list[str]) -> subprocess.CompletedProcess[str]:
    print("+ " + " ".join(command))
    return subprocess.run(command, text=True, check=True)


def git_status_paths(paths: list[Path]) -> set[Path]:
    result = subprocess.run(
        ["git", "status", "--porcelain=v1", "-z", "--", *(str(path) for path in paths)],
        text=True,
        capture_output=True,
        check=True,
    )

    changed_paths: set[Path] = set()
    entries = result.stdout.split("\0")
    index = 0
    while index < len(entries):
        entry = entries[index]
        index += 1

        if not entry:
            continue

        status = entry[:2]
        path = entry[3:]
        changed_paths.add(Path(path))

        if status[0] in {"R", "C"} or status[1] in {"R", "C"}:
            index += 1

    return changed_paths


def content_files() -> list[Path]:
    return sorted(
        path
        for path in CONTENT_DIR.rglob(CONTENT_FILE_GLOB)
        if path.is_file()
    )


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


def upsert_front_matter_field(text: str, field: str, value: str) -> str:
    newline = "\r\n" if "\r\n" in text else "\n"
    lines = text.splitlines(keepends=False)

    if len(lines) < 2 or lines[0] not in {"+++", "---"}:
        raise ValueError("expected TOML or YAML front matter")

    delimiter = lines[0]
    is_toml = delimiter == "+++"

    try:
        end_index = lines.index(delimiter, 1)
    except ValueError as error:
        raise ValueError(f"missing closing {delimiter} front matter delimiter") from error

    replacement = f'{field} = "{value}"' if is_toml else f"{field}: {value}"
    field_prefix = f"{field} " if is_toml else f"{field}:"
    for index in range(1, end_index):
        if lines[index].lstrip().startswith(field_prefix):
            lines[index] = replacement
            return newline.join(lines) + (newline if text.endswith(("\n", "\r\n")) else "")

    insert_index = 1
    for index in range(1, end_index):
        stripped_line = lines[index].lstrip()
        if stripped_line.startswith("date " if is_toml else "date:"):
            insert_index = index + 1
            break
        if stripped_line.startswith("title " if is_toml else "title:"):
            insert_index = index + 1

    lines.insert(insert_index, replacement)
    return newline.join(lines) + (newline if text.endswith(("\n", "\r\n")) else "")


def update_lastmod_fields() -> None:
    changed_paths = git_status_paths([CONTENT_DIR])
    timestamp = datetime.now().astimezone().isoformat(timespec="seconds")

    for path in content_files():
        if path not in changed_paths:
            continue

        text, has_bom = read_text_preserving_bom(path)
        updated_text = upsert_front_matter_field(text, "lastmod", timestamp)
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
