import os
import re
from pathlib import Path

BM_FILE = Path("bm.md")

def main():
    info = os.environ.get("INFO", "").strip()
    url = os.environ.get("URL", "").strip()
    explanation = os.environ.get("EXPLANATION", "").strip()
    tags = os.environ.get("TAGS", "").strip()

    if not all([info, url, explanation, tags]):
        raise ValueError("All fields are required")

    if not re.match(r"^https?://", url):
        raise ValueError("Invalid URL")

    lines = BM_FILE.read_text(encoding="utf-8").splitlines()
    rows = [l for l in lines if l.strip().startswith("|")][2:]

    if any(f"| {url} |" in r for r in rows):
        raise ValueError("Duplicate URL")

    new_row = f"| {info} | {url} | {explanation} | {tags} |"

    insert_at = max(i for i, l in enumerate(lines) if l.strip().startswith("|")) + 1
    lines.insert(insert_at, new_row)
    BM_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("✅ Record added successfully")

if __name__ == "__main__":
    main()
