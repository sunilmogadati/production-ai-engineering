#!/usr/bin/env python3
"""Environment doctor — run this before anything else, and whenever something is odd.

    python3 check_env.py

Checks the things that actually break, in the order they break. Every failure
prints what to do about it. Needs no API key and makes no network calls.

Why this exists: a virtual environment makes exactly one promise -- that `python`
and `pip` serve the same interpreter, so a package you install is a package you
can import. When that promise quietly stops holding, the symptom is bizarre:
pip reports success, python says the module is missing, and every "is my venv
active?" check passes. This finds that case by name.
"""

from __future__ import annotations

import glob
import os
import sys
from pathlib import Path

PASS, WARN, FAIL = "  ok  ", " warn ", " FAIL "
_failed = False


def report(status: str, label: str, detail: str = "", fix: str = "") -> None:
    global _failed
    if status == FAIL:
        _failed = True
    print(f"[{status}] {label}" + (f" — {detail}" if detail else ""))
    if fix:
        for line in fix.strip().splitlines():
            print(f"         {line}")


def check_python_version() -> None:
    major, minor = sys.version_info[:2]
    if (major, minor) >= (3, 10):
        report(PASS, "Python version", f"{major}.{minor}")
    else:
        report(FAIL, "Python version", f"{major}.{minor} — this project needs 3.10+",
               fix="On macOS, /usr/bin/python3 is the system Python and is too old.\n"
                   "Use Homebrew's or python.org's, e.g. $(brew --prefix)/bin/python3.12")


def check_venv_active() -> str | None:
    venv = os.environ.get("VIRTUAL_ENV")
    if not venv:
        report(WARN, "Virtual environment", "none active",
               fix="Not fatal, but you are installing into your system Python.\n"
                   "  cd <repo root> && source .venv/bin/activate")
        return None
    report(PASS, "Virtual environment", venv)
    return venv


def check_interpreter_inside_venv(venv: str | None) -> None:
    if not venv:
        return
    if Path(sys.executable).is_relative_to(Path(venv)):
        report(PASS, "Interpreter is inside the venv", sys.executable)
    else:
        report(FAIL, "Interpreter is NOT inside the venv", sys.executable,
               fix="The venv is active but a different python is running. Usually a PATH\n"
                   "problem or a shim. Rebuild per the instructions at the end.")


def check_single_site_packages(venv: str | None) -> None:
    """The check that catches the failure nobody can diagnose unaided."""
    if not venv:
        return
    trees = sorted(glob.glob(os.path.join(venv, "lib", "python*", "site-packages")))
    running = f"python{sys.version_info.major}.{sys.version_info.minor}"

    if len(trees) <= 1:
        report(PASS, "One site-packages tree", trees[0] if trees else "(none yet)")
        return

    versions = [Path(t).parent.name for t in trees]
    report(FAIL, "Multiple site-packages trees", ", ".join(versions),
           fix=f"This venv serves more than one Python version, and you are running {running}.\n"
               "pip wrote to one tree and python reads another, so installs 'vanish'.\n"
               "The venv is broken. Rebuild it -- reinstalling will not help.")


def check_no_shim_in_chain(venv: str | None) -> None:
    """A shim is a script resolved at call time; a venv assumes a fixed binary."""
    if not venv:
        return
    link = Path(venv) / "bin" / "python3"
    if not link.exists():
        return
    target = os.path.realpath(link)
    if "/shims/" in target or "pyenv" in target and "/versions/" not in target:
        report(FAIL, "venv python is a shim", target,
               fix="A pyenv shim resolves at call time to whatever pyenv currently says --\n"
                   "a venv needs a fixed interpreter. Rebuild naming the binary explicitly.")
    else:
        report(PASS, "venv python is a real interpreter", target)


def check_sdk() -> None:
    try:
        import anthropic
    except ImportError as exc:
        report(FAIL, "anthropic SDK", str(exc), fix="pip install anthropic")
        return
    report(PASS, "anthropic SDK", getattr(anthropic, "__version__", "unknown"))


def check_api_key() -> None:
    key = os.environ.get("ANTHROPIC_API_KEY", "")
    base = os.environ.get("ANTHROPIC_BASE_URL", "")
    if not key:
        report(WARN, "ANTHROPIC_API_KEY", "not set",
               fix="Only the live steps need it; the bench in builds/01-model-routing/src runs\n"
                   "without one.  export ANTHROPIC_API_KEY=sk-ant-...")
    elif len(key) < 40:
        report(WARN, "ANTHROPIC_API_KEY", f"set, but only {len(key)} characters — truncated?")
    else:
        report(PASS, "ANTHROPIC_API_KEY", f"set ({len(key)} chars)")

    if base:
        report(WARN, "ANTHROPIC_BASE_URL", base,
               fix="This points the SDK at a proxy. With your own key you want it UNSET:\n"
                   "  unset ANTHROPIC_BASE_URL")


def check_offline_bench() -> None:
    """Proves the repo itself is runnable, with no key and no network."""
    src = Path(__file__).parent / "builds" / "01-model-routing" / "src"
    if not src.exists():
        report(WARN, "Repository layout", "builds/01-model-routing/src not found",
               fix="Run this from the repository root.")
        return
    sys.path.insert(0, str(src))
    try:
        import pricing
        cost = pricing.cost_usd("claude-opus-5", 1_000_000, 10_000)
        assert abs(cost - 5.25) < 1e-9, cost
        report(PASS, "Offline bench imports and computes", f"1M in + 10k out on opus = ${cost:.2f}")
    except Exception as exc:  # noqa: BLE001
        report(FAIL, "Offline bench", f"{type(exc).__name__}: {exc}")
    finally:
        sys.path.pop(0)


def main() -> int:
    print("\n  Environment check\n")
    check_python_version()
    venv = check_venv_active()
    check_interpreter_inside_venv(venv)
    check_single_site_packages(venv)
    check_no_shim_in_chain(venv)
    check_sdk()
    check_api_key()
    check_offline_bench()

    print()
    if _failed:
        print("  Something is wrong. To rebuild the environment from scratch,")
        print("  FROM THE REPOSITORY ROOT and with no venv active:\n")
        print("      deactivate                 # repeat until no (venv) prefix remains")
        print("      rm -rf .venv")
        print("      $(brew --prefix)/bin/python3.12 -m venv .venv   # name it explicitly")
        print("      source .venv/bin/activate")
        print("      pip install anthropic")
        print("      python3 check_env.py\n")
        return 1

    print("  Ready. Next: see RUN.md\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
