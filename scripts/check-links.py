"""Fail if any local link or image in the Markdown files points at a file that doesn't exist.

Usage: python3 scripts/check-links.py
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
LINK = re.compile(r"\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)|<img[^>]+src=\"([^\"]+)\"")
SKIP = ("http://", "https://", "mailto:", "#")

missing = []
for md in sorted(ROOT.rglob("*.md")):
    if ".git" in md.parts:
        continue
    for match in LINK.finditer(md.read_text(encoding="utf-8")):
        target = match.group(1) or match.group(2)
        if target.startswith(SKIP):
            continue
        path = target.split("#", 1)[0]
        if not (md.parent / path).exists():
            missing.append(f"{md.relative_to(ROOT)}: {target}")

if missing:
    print("Broken local links:")
    print("\n".join(missing))
    sys.exit(1)
print("All local links resolve.")
