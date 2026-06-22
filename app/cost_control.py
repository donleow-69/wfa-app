"""Global Anthropic API spend cap — ledger, pricing, and the free-tier kill switch.

Storage: the existing SQLAlchemy DB (SQLite locally, Postgres on Render via
DATABASE_URL — no Redis in the stack). The monthly counter lives in a single
``spend_ledger`` row per calendar month (see app/models/spend.py). Increments
use ``UPDATE ... SET spend_usd = spend_usd + :delta``, which both SQLite and
Postgres execute under a row lock — safe under concurrent requests without
needing Redis INCR.
"""

from datetime import datetime, timezone

from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from .models.spend import SpendLedger

# Per-million-token USD rates (https://platform.claude.com/docs/en/about-claude/pricing).
# Keep this table in sync with current Anthropic pricing — it's the single source
# of truth for cost calculations.
MODEL_RATES = {
    "claude-haiku-4-5": {
        "input": 1.00,
        "output": 5.00,
        "cache_write": 1.25,
        "cache_read": 0.10,
    },
    "claude-sonnet-4-6": {
        "input": 3.00,
        "output": 15.00,
        "cache_write": 3.75,
        "cache_read": 0.30,
    },
}

# Hard cap on total monthly Anthropic spend.
MONTHLY_CAP_USD = 1000.0

# Free-tier calls stop once month-to-date spend reaches this (safety margin below the cap).
KILL_SWITCH_THRESHOLD_USD = 900.0

# Free tier: cheapest current model, with a hard output cap to bound per-call cost.
FREE_TIER_MODEL = "claude-haiku-4-5"
FREE_TIER_MAX_TOKENS = 600


def current_month() -> str:
    """Current UTC calendar month as 'YYYY-MM' — the ledger key. Rolls over automatically."""
    return datetime.now(timezone.utc).strftime("%Y-%m")


def compute_cost_usd(model: str, usage) -> float:
    """Compute the real USD cost of one Anthropic API call from its response.usage block."""
    rates = MODEL_RATES.get(model)
    if rates is None:
        raise ValueError(f"No pricing configured for model {model!r} — add it to MODEL_RATES")

    input_tokens = getattr(usage, "input_tokens", 0) or 0
    output_tokens = getattr(usage, "output_tokens", 0) or 0
    cache_write_tokens = getattr(usage, "cache_creation_input_tokens", 0) or 0
    cache_read_tokens = getattr(usage, "cache_read_input_tokens", 0) or 0

    return (
        input_tokens * rates["input"]
        + output_tokens * rates["output"]
        + cache_write_tokens * rates["cache_write"]
        + cache_read_tokens * rates["cache_read"]
    ) / 1_000_000


async def record_spend(db: AsyncSession, model: str, usage) -> None:
    """Add the real cost of one API call to this month's ledger row.

    Atomic: a single UPDATE ... SET spend_usd = spend_usd + :delta is row-locked by
    the DB. If this is the first call of the month, the row doesn't exist yet — insert
    it, falling back to the UPDATE if another concurrent request inserted it first.
    """
    cost = compute_cost_usd(model, usage)
    month = current_month()

    result = await db.execute(
        update(SpendLedger).where(SpendLedger.month == month).values(spend_usd=SpendLedger.spend_usd + cost)
    )
    if result.rowcount == 0:
        db.add(SpendLedger(month=month, spend_usd=cost))
        try:
            await db.flush()
        except IntegrityError:
            await db.rollback()
            await db.execute(
                update(SpendLedger)
                .where(SpendLedger.month == month)
                .values(spend_usd=SpendLedger.spend_usd + cost)
            )
    await db.commit()


async def get_month_spend(db: AsyncSession) -> float:
    """Current month-to-date Anthropic API spend in USD."""
    result = await db.execute(select(SpendLedger.spend_usd).where(SpendLedger.month == current_month()))
    return result.scalar_one_or_none() or 0.0


async def kill_switch_active(db: AsyncSession) -> bool:
    """True once month-to-date spend has reached the free-tier kill-switch threshold."""
    return await get_month_spend(db) >= KILL_SWITCH_THRESHOLD_USD
