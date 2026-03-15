from datetime import datetime
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parent
META = ROOT / "content" / "meta.md"


def git(cmd):
    print("> " + " ".join(cmd))
    r = subprocess.run(cmd, cwd=ROOT)
    if r.returncode != 0:
        sys.exit(r.returncode)


def get_frontmatter_and_body(text: str):
    if not text.startswith("---"):
        return "", text

    parts = text.split("---", 2)
    if len(parts) < 3:
        return "", text

    front = "---" + parts[1] + "---\n"
    body = parts[2].lstrip("\n")
    return front, body


def append_entry(commit, desc):
    raw = META.read_text(encoding="utf-8")

    front, body = get_frontmatter_and_body(raw)

    ts = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M %z")
    ts = ts[:-2] + ":" + ts[-2:]

    entry = f"\n<h3> {ts} - {commit}</h3>\n\n{desc}\n"

    if "# Changelog" in body:
        head, tail = body.split("# Changelog", 1)
        new_body = head + "# Changelog\n" + entry + tail.lstrip("\n")
    else:
        new_body = body.rstrip() + "\n\n# Changelog\n" + entry

    META.write_text(front + new_body, encoding="utf-8")


def main():
    print("\n=== CHANGELOG + PUSH ===\n")

    if not META.exists():
        print("meta.md not found")
        sys.exit(1)

    commit = input("Commit title: ").strip()
    if not commit:
        sys.exit(1)

    desc = input("Describe change: ").strip() or commit

    git(["git", "add", "-A"])

    r = subprocess.run(
        ["git", "diff", "--cached", "--quiet"],
        cwd=ROOT,
    )
    if r.returncode == 0:
        print("No changes.")
        return

    print("Updating changelog…")
    append_entry(commit, desc)

    git(["git", "add", "-A"])
    git(["git", "commit", "-m", commit])
    git(["git", "push", "-u", "origin", "main"])

    print("\nDone.")


if __name__ == "__main__":
    main()