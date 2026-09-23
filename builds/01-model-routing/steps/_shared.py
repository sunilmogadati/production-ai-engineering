"""Shared helpers for the model-selection steps.

Deliberately tiny. Everything here exists so the numbered steps can stay about
one idea each instead of re-implementing plumbing.
"""

from __future__ import annotations

import os
import sys
import time
from dataclasses import dataclass

def _mismatch_hint(venv: str) -> str:
    """Say plainly if the package is installed in a SIBLING version tree.

    This is the failure that looks impossible: pip reports success, python says
    the module is missing, and the interpreter IS inside the venv you activated --
    so "is your venv active?" checks all pass. The venv has two
    lib/pythonX.Y/site-packages trees and the two tools disagree about which one
    they serve. Naming the two versions turns a baffling error into an obvious one.
    """
    import glob
    import os

    if not venv or venv == "(none active)":
        return ""

    found = sorted(glob.glob(os.path.join(venv, "lib", "python*", "site-packages", "anthropic")))
    if not found:
        return ""

    installed_under = os.path.basename(os.path.dirname(os.path.dirname(found[0])))
    import sys
    running = f"python{sys.version_info.major}.{sys.version_info.minor}"
    if installed_under == running:
        return ""

    return (
        f"  >>> FOUND IT: anthropic IS installed, under {installed_under}, but you are\n"
        f"      running {running}. Same venv, two site-packages trees -- pip wrote to one\n"
        f"      and python reads the other. The venv is broken; reinstalling will not help.\n\n"
    )


def _import_anthropic():
    """Import the SDK, and on failure say something actually useful.

    A bare `except ImportError: print("pip install anthropic")` is wrong often
    enough to be harmful: the commonest cause of this failure is a venv whose
    `pip` and `python` disagree about which interpreter they serve (pyenv shims
    and nested venvs both cause it). In that case the package IS installed and
    the advice to install it again sends you in a circle.

    So: report the real error, and show which interpreter is actually running.
    """
    try:
        import anthropic
        return anthropic
    except ImportError as exc:
        import sys, os
        venv = os.environ.get("VIRTUAL_ENV", "(none active)")
        sys.exit(
            f"Could not import the Anthropic SDK: {exc}\n\n"
            f"  running python : {sys.executable}\n"
            f"  VIRTUAL_ENV    : {venv}\n"
            f"  looking in     : {[p for p in sys.path if 'site-packages' in p] or 'no site-packages on sys.path'}\n\n"
            f"{_mismatch_hint(venv)}"
            "A venv breaks this way when it is created while another venv is active, or when a\n"
            "pyenv shim resolves `python3` to a different version than pyvenv.cfg records.\n"
            "Fix -- rebuild it with an EXPLICIT interpreter, from outside any active venv:\n"
            "    deactivate            # repeat until no (venv) prefix remains\n"
            "    rm -rf .venv\n"
            "    $(brew --prefix)/bin/python3.12 -m venv .venv    # or any python3.10+ you trust\n"
            "    source .venv/bin/activate && pip install anthropic\n"
            "  Do NOT create a venv while another one is active, and avoid a pyenv-shimmed\n"
            "  `python3` -- a shim can resolve to a different version than pyvenv.cfg records.\n\n"
            "If it IS the right interpreter, then it simply is not installed:  pip install anthropic"
        )


anthropic = _import_anthropic()

# Current model identifiers, verified 2026-09-16. These strings are complete as
# written -- appending a date suffix produces a model that does not exist.
OPUS = "claude-opus-5"
SONNET = "claude-sonnet-5"
HAIKU = "claude-haiku-4-5"

# Dollars per million tokens, same source as ../src/pricing.py.
RATES = {
    OPUS:   {"in": 5.00, "out": 25.00},
    SONNET: {"in": 2.00, "out": 10.00},
    HAIKU:  {"in": 1.00, "out":  5.00},
}


def client() -> "anthropic.Anthropic":
    """An API client, with a readable error when the key is missing."""
    if not os.environ.get("ANTHROPIC_API_KEY"):
        sys.exit(
            "ANTHROPIC_API_KEY is not set.\n"
            "  export ANTHROPIC_API_KEY=sk-ant-...\n"
            "Only these steps need it. The bench in ../src/ runs with no key at all."
        )
    return anthropic.Anthropic()


def cost_usd(model: str, usage) -> float:
    """Price a call from what the API says it actually used.

    Note this reads usage off the RESPONSE rather than estimating. The model
    decides how many output tokens to spend, so the only honest cost is the
    reported one.
    """
    rate = RATES[model]
    return (usage.input_tokens * rate["in"] + usage.output_tokens * rate["out"]) / 1_000_000


@dataclass
class Result:
    """One call, with everything needed to compare it against another."""

    model: str
    text: str
    seconds: float
    input_tokens: int
    output_tokens: int
    cost: float


def call(model: str, system: str, prompt: str, max_tokens: int = 1024, effort: str | None = None) -> Result:
    """One request, timed and priced.

    `effort` trades thoroughness against token spend WITHIN a model. It is the
    lever to reach for before adding a second model -- which is the whole point
    of step 03. Not every tier accepts it, so it is only sent when asked for.
    """
    kwargs = {
        "model": model,
        "max_tokens": max_tokens,
        "system": system,
        "messages": [{"role": "user", "content": prompt}],
    }
    if effort:
        kwargs["output_config"] = {"effort": effort}

    started = time.time()
    response = client().messages.create(**kwargs)
    elapsed = time.time() - started

    text = "".join(b.text for b in response.content if b.type == "text")
    return Result(
        model=model,
        text=text.strip(),
        seconds=elapsed,
        input_tokens=response.usage.input_tokens,
        output_tokens=response.usage.output_tokens,
        cost=cost_usd(model, response.usage),
    )


def row(label: str, r: Result) -> str:
    """One comparison line. Cost is shown to 6 places because these are cents."""
    return (
        f"  {label:<22} {r.seconds:>6.2f}s  "
        f"in={r.input_tokens:>6}  out={r.output_tokens:>5}  ${r.cost:>9.6f}"
    )
