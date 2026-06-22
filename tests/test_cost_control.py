"""Tests for the global spend ledger and free-tier kill switch."""

from types import SimpleNamespace

import pytest

from app.cost_control import (
    FREE_TIER_MODEL,
    KILL_SWITCH_THRESHOLD_USD,
    MODEL_RATES,
    compute_cost_usd,
    current_month,
    get_month_spend,
    kill_switch_active,
    record_spend,
)
from app.models.spend import SpendLedger


def _usage(input_tokens=0, output_tokens=0, cache_creation_input_tokens=0, cache_read_input_tokens=0):
    return SimpleNamespace(
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        cache_creation_input_tokens=cache_creation_input_tokens,
        cache_read_input_tokens=cache_read_input_tokens,
    )


def test_compute_cost_usd_haiku():
    rates = MODEL_RATES[FREE_TIER_MODEL]
    usage = _usage(input_tokens=1_000_000, output_tokens=1_000_000)
    cost = compute_cost_usd(FREE_TIER_MODEL, usage)
    assert cost == pytest.approx(rates["input"] + rates["output"])


def test_compute_cost_usd_includes_cache_tokens():
    usage = _usage(
        input_tokens=1_000_000,
        output_tokens=1_000_000,
        cache_creation_input_tokens=1_000_000,
        cache_read_input_tokens=1_000_000,
    )
    rates = MODEL_RATES[FREE_TIER_MODEL]
    expected = rates["input"] + rates["output"] + rates["cache_write"] + rates["cache_read"]
    assert compute_cost_usd(FREE_TIER_MODEL, usage) == pytest.approx(expected)


def test_compute_cost_usd_unknown_model_raises():
    with pytest.raises(ValueError):
        compute_cost_usd("not-a-real-model", _usage(input_tokens=1))


async def test_record_spend_creates_and_accumulates(db_session):
    usage = _usage(input_tokens=1_000_000, output_tokens=0)  # $1 for Haiku

    await record_spend(db_session, FREE_TIER_MODEL, usage)
    assert await get_month_spend(db_session) == pytest.approx(1.0)

    await record_spend(db_session, FREE_TIER_MODEL, usage)
    assert await get_month_spend(db_session) == pytest.approx(2.0)

    result = await db_session.execute(
        SpendLedger.__table__.select().where(SpendLedger.month == current_month())
    )
    rows = result.fetchall()
    assert len(rows) == 1  # one row per month, not one per call


async def test_get_month_spend_defaults_to_zero(db_session):
    assert await get_month_spend(db_session) == 0.0


async def test_kill_switch_inactive_below_threshold(db_session):
    await record_spend(db_session, FREE_TIER_MODEL, _usage(input_tokens=1_000_000))
    assert await kill_switch_active(db_session) is False


async def test_kill_switch_active_at_threshold(db_session):
    db_session.add(SpendLedger(month=current_month(), spend_usd=KILL_SWITCH_THRESHOLD_USD))
    await db_session.commit()
    assert await kill_switch_active(db_session) is True
