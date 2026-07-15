#!/usr/bin/env python3
"""Lightweight repo validation for the teaching repository.

Checks, without touching Postgres or starting a server:

1. Files listed in AGENT_CONTEXT.json (docs + code entry points + infra) exist.
2. Every main*.py file compiles (syntax check via py_compile).
3. Local markdown links in root .md files resolve to real files.

Run from the repo root:

    python3 scripts/validate_repo.py

Exit code 0 means all checks passed; non-zero means something needs attention.
Uses only the Python standard library so it is safe to run in CI.
"""

from __future__ import annotations

import json
import py_compile
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Matches [text](target) markdown links.
MD_LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")


def _rel(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def check_context_files(errors: list[str]) -> None:
    """Every path named in AGENT_CONTEXT.json should exist."""
    context_path = REPO_ROOT / "AGENT_CONTEXT.json"
    if not context_path.exists():
        errors.append("AGENT_CONTEXT.json is missing")
        return

    context = json.loads(context_path.read_text())

    def flatten(value) -> list[str]:
        """Collect string file references from strings and lists of strings."""
        if isinstance(value, str):
            return [value]
        if isinstance(value, list):
            return [item for item in value if isinstance(item, str)]
        return []

    referenced: list[str] = []
    for section in ("documentation", "infrastructure", "entryPoints"):
        for value in context.get(section, {}).values():
            referenced.extend(flatten(value))

    for ref in referenced:
        if not (REPO_ROOT / ref).exists():
            errors.append(f"AGENT_CONTEXT.json references missing file: {ref}")


def check_python_compiles(errors: list[str]) -> None:
    """All demo files (API, hello, and ML tiers) must be syntactically valid."""
    demos: list[Path] = []
    for pattern in ("main*.py", "hello_*.py", "ml*.py", "ai*.py"):
        demos.extend(REPO_ROOT.glob(pattern))
    demos = sorted(set(demos))
    if not demos:
        errors.append("no demo python files found")
    for demo in demos:
        try:
            py_compile.compile(str(demo), doraise=True)
        except py_compile.PyCompileError as exc:
            errors.append(f"syntax error in {_rel(demo)}: {exc.msg}")


def check_markdown_links(errors: list[str]) -> None:
    """Local (non-URL) markdown links in root docs must resolve."""
    for md in sorted(REPO_ROOT.glob("*.md")):
        text = md.read_text()
        for target in MD_LINK.findall(text):
            link = target.strip()
            # Skip external links, anchors, and mail links.
            if link.startswith(("http://", "https://", "#", "mailto:")):
                continue
            # Strip any in-page anchor and query.
            local = link.split("#", 1)[0].split("?", 1)[0].strip()
            if not local:
                continue
            resolved = (md.parent / local).resolve()
            if not resolved.exists():
                errors.append(f"{_rel(md)}: broken link -> {link}")


def main() -> int:
    errors: list[str] = []

    check_context_files(errors)
    check_python_compiles(errors)
    check_markdown_links(errors)

    if errors:
        print("Repo validation FAILED:")
        for err in errors:
            print(f"  - {err}")
        return 1

    print("Repo validation passed: context files, python syntax, and doc links are OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
