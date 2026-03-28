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


def get_staged_files():
    r = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if r.returncode != 0:
        sys.exit(r.returncode)

    files = [line.strip() for line in r.stdout.splitlines() if line.strip()]

    try:
        meta_rel = str(META.relative_to(ROOT)).replace("\\", "/")
        files = [f for f in files if f.replace("\\", "/") != meta_rel]
    except ValueError:
        pass

    return files


def append_entry(commit, desc, changed_files):
    raw = META.read_text(encoding="utf-8")

    front, body = get_frontmatter_and_body(raw)

    ts = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M %z")
    ts = ts[:-2] + ":" + ts[-2:]

    files_text = ""
    if changed_files:
        file_list = ", ".join(changed_files)
        files_text = f"\n\nChanged files: {file_list}"

    entry = f"<p>\n<b> {ts} - {commit}</b>\n\n{desc}{files_text}</p>\n"

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

    changed_files = get_staged_files()

    print("Updating changelog...")
    append_entry(commit, desc, changed_files)

    git(["git", "add", "-A"])
    git(["git", "commit", "-m", commit])
    git(["git", "push", "-u", "origin", "main"])

    print("\nDone.")


if __name__ == "__main__":
    main()