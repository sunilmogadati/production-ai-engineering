"""The publication rules, as executable tests.

A rule that lives only in a document is a rule someone forgets at 11pm. These fail
the build instead.
"""

import re
from pathlib import Path

BUILD = Path(__file__).resolve().parent.parent

# Files to scan: everything a reader could receive.
SCANNED = [
    p
    for p in BUILD.rglob("*")
    if p.is_file()
    and p.suffix in {".py", ".md", ".toml", ".json", ".example", ".txt"}
    and "__pycache__" not in p.parts
]

# An Anthropic key is a long token with a recognisable prefix. The test looks for the
# shape, not a specific value, so it catches a key nobody thought to add to a denylist.
KEY_SHAPES = [
    re.compile(r"sk-ant-[A-Za-z0-9_\-]{20,}"),
    re.compile(r"sk-[A-Za-z0-9]{32,}"),
]


def test_no_credential_appears_in_the_build():
    for path in SCANNED:
        text = path.read_text(encoding="utf-8", errors="ignore")
        for shape in KEY_SHAPES:
            assert not shape.search(text), f"credential-shaped string in {path.name}"


def test_env_example_carries_names_only():
    env = BUILD / ".env.example"
    assert env.exists(), ".env.example is missing"
    for line in env.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        name, _, value = line.partition("=")
        assert value == "", f"{name} carries a value in .env.example"


# The named-source denylist deliberately does NOT live here. A public file listing the
# names it forbids discloses them just as effectively as using them would. That check is
# a pre-publish gate in the private governance repo; what stays public is the structural
# rule below, which needs no vendor name to express.


def test_no_lesson_coordinates_in_file_names():
    # A structural tell defeats a name scrub: a folder set that maps onto a published
    # syllabus is an attribution with the name removed.
    coordinate = re.compile(r"(^|[^a-z])(l\d{1,2}|lesson[-_ ]?\d+|course[-_ ]?\d+)([^a-z]|$)", re.IGNORECASE)
    for path in SCANNED:
        assert not coordinate.search(path.name), f"lesson coordinate in file name {path.name}"
