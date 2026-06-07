"""Fail if there are multiple Alembic head revisions (no DB connection needed)."""

import re
import sys
from pathlib import Path

versions_dir = Path(__file__).parent.parent / "alembic" / "versions"

all_revisions: set[str] = set()
referenced_as_parent: set[str] = set()

for path in versions_dir.glob("*.py"):
    text = path.read_text()

    rev = re.search(r'^revision\s*[:=][^"\']*["\']([^"\']+)["\']', text, re.MULTILINE)
    if rev:
        all_revisions.add(rev.group(1))

    for down in re.finditer(
        r'^down_revision\s*[:=][^"\']*["\']([^"\']+)["\']', text, re.MULTILINE
    ):
        referenced_as_parent.add(down.group(1))

heads = all_revisions - referenced_as_parent

if len(heads) > 1:
    print(f"ERROR: Multiple Alembic heads detected: {heads}")
    print("Fix: set down_revision in your new migration to the current head.")
    sys.exit(1)

print(f"OK: single Alembic head — {heads}")
