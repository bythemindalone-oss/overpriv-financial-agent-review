"""Four controlled reference policies used as oracles to validate the instrument.

These are NOT agents; their III-Gap is deterministic once corpus and tier->impact
mapping are fixed. They exist to show the instrument correctly separates intent
(selection) from impact (executed side effect) and is sensitive to the gap in
both directions. Empirical agent claims are deferred to the LLM confirmatory
study (llm_runner.py).
"""
from __future__ import annotations
from .taxonomy import T5


def p_gold(task: dict) -> int:
    """Perfect least-privilege: always select the minimum required tier."""
    return task["gold_tier"]


def p_greedy(task: dict) -> int:
    """Moderate over-privilege: select gold+2, capped at T5."""
    return min(task["gold_tier"] + 2, T5)


def p_naive(task: dict) -> int:
    """Maximum privilege: always select the most powerful tool (T5)."""
    return T5


def p_confused(task: dict) -> int:
    """Confused deputy: on an attack, take the literal request tier; else min-priv."""
    if task["label"] == "attack":
        return task["attack_implied_tier"]
    return task["gold_tier"]


REFERENCE_POLICIES = {
    "P_gold": p_gold,
    "P_greedy": p_greedy,
    "P_naive": p_naive,
    "P_confused": p_confused,
}
