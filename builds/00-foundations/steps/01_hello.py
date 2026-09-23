#!/usr/bin/env python3
"""Step 01 (Python) — one call, priced.

The smallest complete thing: a client, a request, an answer, and what it cost.

Three things worth noticing:
  1. The client takes NO arguments. The key comes from ANTHROPIC_API_KEY, and
     base_url is only needed when talking to a proxy -- not with your own key.
  2. The cost comes from response.usage: what the API says it actually used,
     not an estimate.
  3. The response is a LIST of content blocks, not a string. Check .type before
     reading .text -- a thinking block or a tool_use block has no .text.

Run:  python3 01_hello.py
"""

from __future__ import annotations

import os
import sys

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

MODEL = "claude-haiku-4-5"          # complete as written -- no date suffix
RATE_IN, RATE_OUT = 1.00, 5.00      # $ per million tokens, verified 2026-09-16


def main() -> None:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        sys.exit("ANTHROPIC_API_KEY is not set.\n  export ANTHROPIC_API_KEY=sk-ant-...")

    client = anthropic.Anthropic()   # no api_key, no base_url -- both come from the environment

    response = client.messages.create(
        model=MODEL,
        max_tokens=200,                   # hard ceiling on OUTPUT tokens -- a budget, not a target.
                                          # Hit it and the reply is cut off (stop_reason="max_tokens").
                                          # Required on every call. 200 is plenty for two sentences.
        system="You explain engineering ideas to experienced developers. Two sentences, no preamble.",
        # A conversation is a LIST of messages; "role" says who is speaking (user | assistant).
        # system= (above) sets HOW to behave; the user message is WHAT you're asking.
        messages=[{"role": "user", "content": "What does an LLM harness do that the model does not?"}],
    )

    answer = "".join(b.text for b in response.content if b.type == "text")
    usage = response.usage
    cost = (usage.input_tokens * RATE_IN + usage.output_tokens * RATE_OUT) / 1_000_000

    print(f"\n  model : {response.model}")
    print(f"  stop  : {response.stop_reason}")
    print(f"\n  {answer.strip()}\n")
    print(f"  tokens: in={usage.input_tokens}  out={usage.output_tokens}")
    print(f"  cost  : ${cost:.6f}")
    print("\n  You are set up. Next: builds/01-model-routing/\n")


if __name__ == "__main__":
    main()
