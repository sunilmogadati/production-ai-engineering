"""Three synthetic tools for an incident-triage agent, plus the plumbing.

Same domain as Build 01, so the only new idea here is the loop itself.

The data is fabricated but deliberately *inconsistent* -- the metrics and the
deploy log disagree about timing. An agent that reconciles them has to make more
than one call, which is the only way a loop earns its existence.
"""

from __future__ import annotations

import json
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

MODEL = "claude-sonnet-5"          # complete as written -- no date suffix
RATE_IN, RATE_OUT = 2.00, 10.00    # $ per MTok, verified 2026-09-16


def client() -> "anthropic.Anthropic":
    if not os.environ.get("ANTHROPIC_API_KEY"):
        sys.exit("ANTHROPIC_API_KEY is not set.\n  export ANTHROPIC_API_KEY=sk-ant-...")
    return anthropic.Anthropic()


def cost_of(usage) -> float:
    return (usage.input_tokens * RATE_IN + usage.output_tokens * RATE_OUT) / 1_000_000


# --- the tool schemas the model reads -------------------------------------
# The description is the only documentation the model gets, and it reads it at
# call time with no chance to ask a follow-up. Vague descriptions are the most
# common cause of a tool being called at the wrong moment.

TOOLS = [
    {
        "name": "get_service_metrics",
        "description": (
            "Latency and error-rate time series for one service over the last N hours. "
            "Use this to establish WHEN a problem started."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "service": {"type": "string", "description": "service name, e.g. checkout-api"},
                "hours": {"type": "integer", "description": "how far back to look, 1-24"},
            },
            "required": ["service"],
        },
    },
    {
        "name": "get_recent_deploys",
        "description": (
            "Deployments for one service, most recent first. "
            "Use this to find a change that could explain a problem you have already located in time."
        ),
        "input_schema": {
            "type": "object",
            "properties": {"service": {"type": "string"}},
            "required": ["service"],
        },
    },
    {
        "name": "get_dependencies",
        "description": (
            "Which other services share infrastructure with this one. "
            "Use this when a problem may originate outside the service reporting it."
        ),
        "input_schema": {
            "type": "object",
            "properties": {"service": {"type": "string"}},
            "required": ["service"],
        },
    },
]

_METRICS = {
    "checkout-api": {
        "p99_ms": [(0, 1800), (-10, 1850), (-20, 4100), (-30, 6400), (-40, 6300), (-50, 1790)],
        "error_rate": [(0, 0.003), (-20, 0.019), (-30, 0.021), (-50, 0.003)],
        "note": "degradation began ~45 minutes ago",
    },
    "payments-svc": {
        "p99_ms": [(0, 240), (-30, 250), (-60, 245)],
        "error_rate": [(0, 0.001), (-60, 0.001)],
        "note": "healthy throughout",
    },
}

_DEPLOYS = {
    # NOTE the inconsistency: checkout-api itself has not deployed in 3 days,
    # but its dependency shipped right before the degradation. An agent that
    # stops after one tool call gets this wrong.
    "checkout-api": [{"version": "v9.2.0", "minutes_ago": 4320, "author": "team-checkout"}],
    "payments-svc": [{"version": "v4.12", "minutes_ago": 55, "author": "team-payments",
                      "summary": "connection pool sizing change"}],
}

_DEPS = {
    "checkout-api": ["payments-svc", "inventory-svc"],
    "payments-svc": ["postgres-primary"],
}


def run_tool(name: str, args: dict) -> str:
    """Execute a tool. Returns a JSON string, which is what goes back to the model."""
    service = args.get("service", "")
    if name == "get_service_metrics":
        data = _METRICS.get(service)
        return json.dumps(data or {"error": f"no metrics for {service!r}"})
    if name == "get_recent_deploys":
        return json.dumps(_DEPLOYS.get(service, []))
    if name == "get_dependencies":
        return json.dumps({"service": service, "shares_infra_with": _DEPS.get(service, [])})
    return json.dumps({"error": f"unknown tool {name!r}"})


INCIDENT = (
    "checkout-api p99 latency jumped and error rate is up. "
    "Find the most likely cause and say what you would check next."
)

SYSTEM = (
    "You are a staff engineer triaging a production incident. "
    "Use the tools to gather evidence before concluding. "
    "When you have a hypothesis, state it plainly with the evidence that supports it."
)
