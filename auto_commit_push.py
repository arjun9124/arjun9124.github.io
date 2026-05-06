#!/usr/bin/env python3
"""Commit and push all changes with an incrementing numeric commit title."""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parent
DEFAULT_COMMIT_TITLE = 11340507042043
CHANGELOG_FILE = Path("content/changelog.md")
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
    return subprocess.run(command, cwd=ROOT, text=True, check=True)


def relative_path(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def git_status_paths(paths: list[Path]) -> set[Path]:
    result = subprocess.run(
        ["git", "status", "--porcelain", "--", *(str(path) for path in paths)],
        cwd=ROOT,
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
    path = relative_path(path)
    raw = path.read_bytes()
    has_bom = raw.startswith(b"\xef\xbb\xbf")
    if has_bom:
        raw = raw[3:]
    return raw.decode("utf-8"), has_bom


def write_text_preserving_bom(path: Path, text: str, has_bom: bool) -> None:
    path = relative_path(path)
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
    existing_files = [path for path in LASTMOD_FILES if relative_path(path).exists()]
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


def timestamp_for_changelog(now: datetime) -> str:
    timestamp = now.strftime("%Y-%m-%d %H:%M %z")
    return timestamp[:-2] + ":" + timestamp[-2:]


def git_status_lines() -> list[str]:
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    return result.stdout.splitlines()


def changed_files_for_summary() -> list[Path]:
    files: list[Path] = []
    for line in git_status_lines():
        path = line[3:]
        if " -> " in path:
            path = path.rsplit(" -> ", 1)[1]
        if path and path != str(CHANGELOG_FILE):
            files.append(Path(path))
    return files


def autogen_changelog_title(files: list[Path]) -> str:
    if not files:
        return "Site update"

    top_level = sorted({path.parts[0] for path in files if path.parts})
    if top_level == ["content"]:
        sections = sorted({path.parts[1] for path in files if len(path.parts) > 2})
        if sections:
            return "Updated " + ", ".join(sections[:3])
        return "Updated content"

    return "Updated " + ", ".join(top_level[:3])


def autogen_changelog_comment(files: list[Path]) -> str:
    if not files:
        return "Updated the site."

    shown_files = ", ".join(str(path).replace("\\", "/") for path in files[:5])
    if len(files) > 5:
        shown_files += f", and {len(files) - 5} more"

    return f"Updated {shown_files}."


def prompt_optional(prompt: str) -> str:
    if not sys.stdin.isatty():
        return ""

    try:
        return input(prompt).strip()
    except EOFError:
        return ""


def upsert_changelog_entry(title: str, comment: str) -> None:
    changelog_path = relative_path(CHANGELOG_FILE)
    text, has_bom = read_text_preserving_bom(changelog_path)
    now = datetime.now().astimezone()
    entry = f"<p>\n<b> {timestamp_for_changelog(now)} - {title}</b>\n\n{comment}</p>\n"

    marker = "<!-- CHNG -->"
    if marker in text:
        head, tail = text.split(marker, 1)
        updated_text = head + marker + "\n" + entry + tail.lstrip("\n")
    else:
        updated_text = text.rstrip() + "\n\n" + marker + "\n" + entry

    write_text_preserving_bom(changelog_path, updated_text, has_bom)


def update_changelog(title: str | None, comment: str | None, prompt: bool) -> None:
    files = changed_files_for_summary()
    if not files:
        return

    generated_title = autogen_changelog_title(files)
    generated_comment = autogen_changelog_comment(files)

    if prompt:
        title = title or prompt_optional(f"Changelog title [{generated_title}]: ")
        comment = comment or prompt_optional(f"Changelog comment [{generated_comment}]: ")

    upsert_changelog_entry(
        title.strip() if title else generated_title,
        comment.strip() if comment else generated_comment,
    )


def latest_commit_title() -> str | None:
    result = subprocess.run(
        ["git", "log", "-1", "--pretty=%s"],
        cwd=ROOT,
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
    parser.add_argument(
        "--changelog-title",
        help="Optional title for the generated changelog entry.",
    )
    parser.add_argument(
        "--changelog-comment",
        help="Optional comment/body for the generated changelog entry.",
    )
    parser.add_argument(
        "--no-changelog",
        action="store_true",
        help="Skip writing the generated changelog entry.",
    )
    parser.add_argument(
        "--no-changelog-prompt",
        action="store_true",
        help="Use autogenerated changelog text without prompting.",
    )
    args = parser.parse_args()

    commit_title = next_commit_title(args.start)

    try:
        if not args.no_changelog:
            update_changelog(
                args.changelog_title,
                args.changelog_comment,
                prompt=not args.no_changelog_prompt,
            )
        update_lastmod_fields()
        run(["git", "add", "-A"])
        run(["git", "commit", "-m", commit_title])
        run(["git", "push", "-u", args.remote, args.branch])
    except subprocess.CalledProcessError as error:
        return error.returncode

    return 0


if __name__ == "__main__":
    sys.exit(main())
