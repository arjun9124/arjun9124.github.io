from __future__ import annotations

import subprocess
import sys
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parent
META_FILE = ROOT / "content" / "meta.md"


def run(cmd: list[str]) -> None:
    print(f"\n> {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=ROOT)
    if result.returncode != 0:
        print(f"ERROR: command failed with exit code {result.returncode}")
        sys.exit(result.returncode)


def git_has_staged_changes() -> bool:
    result = subprocess.run(
        ["git", "diff", "--cached", "--quiet"],
        cwd=ROOT,
    )
    return result.returncode != 0


def ensure_meta_file() -> None:
    if not META_FILE.exists():
        print(f"ERROR: {META_FILE} not found")
        sys.exit(1)


def append_changelog_entry(commit_name: str, description: str) -> None:
    text = META_FILE.read_text(encoding="utf-8")

    heading = "# Changelog"
    timestamp = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M %z")
    timestamp = f"{timestamp[:-2]}:{timestamp[-2:]}"  # +0530 -> +05:30

    entry = (
        f"\n### {timestamp} - {commit_name}\n\n"
        f"{description}\n"
    )

    if heading in text:
        idx = text.index(heading) + len(heading)
        new_text = text[:idx] + "\n" + entry + text[idx:]
    else:
        new_text = text.rstrip() + f"\n\n# Changelog\n" + entry

    META_FILE.write_text(new_text, encoding="utf-8", newline="\n")


def main() -> None:
    print("\n==== SITE CHANGELOG + PUSH ====\n")

    ensure_meta_file()

    commit_name = input("Commit title: ").strip()
    if not commit_name:
        print("ERROR: Commit title required.")
        sys.exit(1)

    description = input("Describe change: ").strip()
    if not description:
        description = commit_name

    run(["git", "add", "-A"])

    if not git_has_staged_changes():
        print("No changes detected.")
        sys.exit(0)

    print("\nWriting changelog entry...")
    append_changelog_entry(commit_name, description)

    run(["git", "add", "-A"])
    run(["git", "commit", "-m", commit_name])
    run(["git", "push", "-u", "origin", "main"])

    print("\nDone.")


if __name__ == "__main__":
    main()
