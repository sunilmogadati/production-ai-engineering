"""Cost arithmetic, checked against values computed by hand.

These tests make the build's central claim defensible: you can know what a workload
costs before you spend anything. They run with no API key and no network.
"""

import pytest

import pricing


def test_opus_cost_matches_hand_computed():
    # 1,000,000 input @ $5.00/MTok = $5.00
    #    10,000 output @ $25.00/MTok = $0.25
    assert pricing.cost_usd("claude-opus-5", 1_000_000, 10_000) == pytest.approx(5.25)


def test_sonnet_cost_matches_hand_computed():
    # 500,000 input @ $2.00/MTok = $1.00 ; 20,000 output @ $10.00/MTok = $0.20
    assert pricing.cost_usd("claude-sonnet-5", 500_000, 20_000) == pytest.approx(1.20)


def test_haiku_cost_matches_hand_computed():
    # 100,000 input @ $1.00/MTok = $0.10 ; 2,000 output @ $5.00/MTok = $0.01
    assert pricing.cost_usd("claude-haiku-4-5", 100_000, 2_000) == pytest.approx(0.11)


def test_zero_tokens_costs_nothing():
    assert pricing.cost_usd("claude-opus-5", 0, 0) == 0.0


def test_unknown_model_fails_loudly():
    # A typo in a model id must not silently price as something else.
    with pytest.raises(KeyError):
        pricing.cost_usd("claude-opus-5-20260401", 100, 100)


def test_no_model_id_carries_a_date_suffix():
    # Date-suffixed identifiers are a habit from older model families and produce
    # a model that does not exist. Constitution VIII.
    for model in pricing.MODELS.values():
        assert not model.model_id[-8:].isdigit(), model.model_id


def test_rate_table_declares_when_it_was_taken():
    # A rate table with no date is a rate table nobody can tell is stale.
    assert pricing.RATES_TAKEN_ON
    assert pricing.RATES_SOURCE


def test_context_window_is_a_hard_constraint():
    assert pricing.fits_context("claude-haiku-4-5", 200_000)
    assert not pricing.fits_context("claude-haiku-4-5", 200_001)
    assert pricing.fits_context("claude-opus-5", 1_000_000)
