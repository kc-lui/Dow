"""Fetch daily OHLCV from Stooq's CSV endpoint (fallback source)."""

from __future__ import annotations

import io
import logging

import pandas as pd
import requests

from dowtheory.data.bars import normalize_bars

logger = logging.getLogger(__name__)
SOURCE = "stooq"
HOSTS = ("https://stooq.com", "https://stooq.pl")
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)
STOOQ_SYMBOLS = {
    "^DJI": "^dji", "^DJT": "^djt", "^GSPC": "^spx", "^IXIC": "^ndq",
    "SPY": "spy.us", "IYT": "iyt.us",
}


class SourceUnavailable(RuntimeError):
    """The data source answered with an error status or no data."""


def fetch_daily(symbol: str, exchange: str | None = None, timeout: float = 20.0) -> pd.DataFrame:
    """Try each Stooq host once; raise SourceUnavailable when none returns data."""
    code = STOOQ_SYMBOLS.get(symbol, symbol.lower())
    failures: list[str] = []
    for host in HOSTS:
        url = f"{host}/q/d/l/?s={code}&i=d"
        try:
            resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=timeout)
        except requests.RequestException as exc:
            failures.append(f"{url}: {exc}")
            continue
        text = resp.text.strip()
        if resp.status_code != 200:
            failures.append(f"{url}: HTTP {resp.status_code}")
        elif not text or text.lower().startswith("no data") or "Date" not in text.split("\n")[0]:
            failures.append(f"{url}: empty or non-CSV body ({text[:40]!r})")
        else:
            raw = pd.read_csv(io.StringIO(text))
            try:
                return normalize_bars(raw, symbol, SOURCE, exchange)
            except ValueError as exc:
                failures.append(f"{url}: {exc}")
    raise SourceUnavailable(f"Stooq unavailable for {symbol}: " + "; ".join(failures))
