"""
Databento data preparation utilities.

The module keeps the empirical design in code so that the sample definition
does not depend on manually selected dates.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np
import pandas as pd


ANCHOR_DATES = pd.to_datetime([
    "2022-01-03","2022-02-01","2022-03-01","2022-04-01","2022-05-02","2022-06-01",
    "2022-07-01","2022-08-01","2022-09-01","2022-10-03","2022-11-01","2022-12-01",
    "2023-01-03","2023-02-01","2023-03-01","2023-04-03","2023-05-01","2023-06-01",
    "2023-07-03","2023-08-01","2023-09-01","2023-10-02","2023-11-01","2023-12-01",
    "2024-01-02","2024-02-01","2024-03-01","2024-04-01","2024-05-01","2024-06-03",
    "2024-07-01","2024-08-01","2024-09-03","2024-10-01","2024-11-01","2024-12-02",
    "2025-01-02","2025-02-03","2025-03-03","2025-04-01","2025-05-01","2025-06-02",
    "2025-07-01","2025-08-01","2025-09-02","2025-10-01","2025-11-03","2025-12-01",
]).normalize()


def anchor_schedule() -> pd.DataFrame:
    """Return the 48 pre-specified monthly anchor observations."""
    return pd.DataFrame({
        "observation": np.arange(1, len(ANCHOR_DATES) + 1),
        "anchor_date": ANCHOR_DATES,
    })


def _read(path: str) -> pd.DataFrame:
    return pd.read_parquet(path) if str(path).endswith(".parquet") else pd.read_csv(path)


def clean_nbbo_quotes(quotes: pd.DataFrame) -> pd.DataFrame:
    """
    Clean OPRA quote data and construct NBBO midpoints.

    Required columns: ts_event, underlying, option_type, strike, expiry, bid, ask.
    """
    required = {
        "ts_event", "underlying", "option_type",
        "strike", "expiry", "bid", "ask"
    }
    missing = required.difference(quotes.columns)
    if missing:
        raise ValueError(f"Missing option fields: {sorted(missing)}")

    q = quotes.copy()
    q["ts_event"] = pd.to_datetime(q["ts_event"], utc=True)
    q["expiry"] = pd.to_datetime(q["expiry"]).dt.normalize()

    for col in ("strike", "bid", "ask"):
        q[col] = pd.to_numeric(q[col], errors="coerce")

    q = q.replace([np.inf, -np.inf], np.nan).dropna(
        subset=["strike", "bid", "ask"]
    )
    q = q[(q["bid"] >= 0) & (q["ask"] >= q["bid"]) & (q["ask"] > 0)]
    q["mid"] = (q["bid"] + q["ask"]) / 2.0
    return q[q["mid"] > 0].reset_index(drop=True)


def select_1559_quotes(
    quotes: pd.DataFrame,
    anchor_date: str,
    expiry: str,
    underlying: str,
) -> pd.DataFrame:
    """Select valid 15:59 ET quotes for one underlying and expiry."""
    q = quotes.copy()
    q["ts_event"] = pd.to_datetime(q["ts_event"], utc=True)
    q["expiry"] = pd.to_datetime(q["expiry"]).dt.normalize()

    local = q["ts_event"].dt.tz_convert("America/New_York")
    anchor = pd.Timestamp(anchor_date).date()
    exp = pd.Timestamp(expiry).normalize()

    out = q[
        (q["underlying"] == underlying)
        & (local.dt.date == anchor)
        & (local.dt.hour == 15)
        & (local.dt.minute == 59)
        & (q["expiry"] == exp)
    ].copy()

    return out.sort_values(["option_type", "strike"]).reset_index(drop=True)


def select_common_expiry(
    definitions: pd.DataFrame,
    anchor_date: str,
    min_dte: int = 35,
    max_dte: int = 60,
    target_dte: int = 45,
) -> pd.Timestamp:
    """
    Select the common QQQ/TQQQ expiry closest to the target DTE.
    """
    required = {"underlying", "expiry"}
    missing = required.difference(definitions.columns)
    if missing:
        raise ValueError(f"Missing definition fields: {sorted(missing)}")

    d = definitions.copy()
    d["expiry"] = pd.to_datetime(d["expiry"]).dt.normalize()
    d = d[d["underlying"].isin(["QQQ", "TQQQ"])]

    common = (
        d.groupby("expiry")["underlying"]
        .nunique()
        .loc[lambda x: x == 2]
        .index
    )

    anchor = pd.Timestamp(anchor_date).normalize()
    candidates = [
        e for e in common
        if min_dte <= (e - anchor).days <= max_dte
    ]
    if not candidates:
        raise ValueError("No common QQQ/TQQQ expiry satisfies the DTE bounds.")

    return min(
        candidates,
        key=lambda e: (abs((e - anchor).days - target_dte), e)
    )


def process_equity_ohlcv(data: pd.DataFrame) -> pd.DataFrame:
    """Standardise an equity OHLCV table with an ET timestamp and close."""
    if "ts_event" not in data or "close" not in data:
        raise ValueError("Equity data must contain ts_event and close.")

    df = data.copy()
    ts = pd.to_datetime(df["ts_event"], utc=True)
    local = ts.dt.tz_convert("America/New_York")
    df["date"] = local.dt.normalize()
    df["close"] = pd.to_numeric(df["close"], errors="coerce")

    return (
        df.dropna(subset=["close"])
        .sort_values("date")
        .drop_duplicates("date", keep="last")
        [["date", "close"]]
        .reset_index(drop=True)
    )


def build_option_surface(
    quotes: pd.DataFrame,
    anchor_date: str,
    expiry: str,
    underlying: str,
    spot: float,
    low_moneyness: float = 0.80,
    high_moneyness: float = 1.20,
) -> pd.DataFrame:
    """
    Build the cleaned option surface used by the research modules.

    Strikes are retained inside the requested spot-moneyness range.
    """
    q = select_1559_quotes(quotes, anchor_date, expiry, underlying)
    q = q[
        (q["strike"] >= low_moneyness * spot)
        & (q["strike"] <= high_moneyness * spot)
    ].copy()

    q["moneyness"] = q["strike"] / float(spot)
    return q.reset_index(drop=True)


def prepare_48_observation_schedule(definitions: pd.DataFrame) -> pd.DataFrame:
    """Attach the selected common expiry and calendar DTE to all 48 anchors."""
    rows = []
    for anchor in ANCHOR_DATES:
        expiry = select_common_expiry(definitions, anchor)
        rows.append({
            "anchor_date": anchor,
            "expiry": expiry,
            "dte": int((expiry - anchor).days),
        })
    return pd.DataFrame(rows)
