"""Guarded ClickHouse client: scoped ``dow_user``, SQL allowlist, writes only into ``dow``."""

from __future__ import annotations

import logging
import os
from typing import Any, Self

import pandas as pd

from dowtheory.storage import sql_guard
from dowtheory.storage.sql_guard import UnsafeSQLError

__all__ = ["ClickHouseClient", "UnsafeSQLError"]

logger = logging.getLogger(__name__)

ALLOWED_DATABASE = sql_guard.WRITE_DB
INSERT_CHUNK_ROWS = 1000  # daily bars: ~48 yearly partitions per block, under the 100 limit
READONLY_SETTINGS = {"readonly": 1}


class ClickHouseClient:
    """Env-driven wrapper around clickhouse-connect. The connection is opened lazily.

    Credentials come from ``DOW_CLICKHOUSE_USER`` (default ``dow_user``) and
    ``DOW_CLICKHOUSE_PASSWORD`` (default ``dow_secret``), never from the admin variables.
    """

    def __init__(
        self,
        host: str | None = None,
        port: int | None = None,
        database: str | None = None,
        user: str | None = None,
        password: str | None = None,
    ) -> None:
        self.database = database or os.getenv("CLICKHOUSE_DATABASE", ALLOWED_DATABASE)
        if self.database != ALLOWED_DATABASE:
            raise UnsafeSQLError(f"Database must be '{ALLOWED_DATABASE}', got '{self.database}'")
        self._params: dict[str, Any] = {
            "host": host or os.getenv("CLICKHOUSE_HOST", "localhost"),
            "port": int(port or os.getenv("CLICKHOUSE_PORT", "8123")),
            "username": user or os.getenv("DOW_CLICKHOUSE_USER", "dow_user"),
            "password": password or os.getenv("DOW_CLICKHOUSE_PASSWORD", "dow_secret"),
            "database": self.database,
        }
        self._client: Any = None

    def _conn(self) -> Any:
        if self._client is None:
            import clickhouse_connect

            self._client = clickhouse_connect.get_client(**self._params)
        return self._client

    def query_df(self, sql: str, params: dict[str, Any] | None = None) -> pd.DataFrame:
        """Run an allowlisted read (server-side ``readonly=1``) and return a DataFrame."""
        sql_guard.check_read(sql)
        return self._conn().query_df(sql, parameters=params, settings=READONLY_SETTINGS)

    def insert_df(self, table: str, df: pd.DataFrame) -> int:
        """Insert ``df`` into ``dow.<table>``; returns the number of rows sent."""
        name = table[len(ALLOWED_DATABASE) + 1 :]
        if not table.startswith(f"{ALLOWED_DATABASE}.") or not name.isidentifier():
            raise UnsafeSQLError(f"Insert target must be 'dow.<table>', got '{table}'")
        if df.empty:
            raise ValueError(f"Refusing to insert an empty frame into {table}")
        for lo in range(0, len(df), INSERT_CHUNK_ROWS):
            self._conn().insert_df(table, df.iloc[lo : lo + INSERT_CHUNK_ROWS])
        return len(df)

    def command(self, sql: str, params: dict[str, Any] | None = None) -> Any:
        """Run an allowlisted write: INSERT, ALTER DELETE/UPDATE, OPTIMIZE, CREATE IF NOT EXISTS,
        EXCHANGE TABLES (all confined to ``dow``).

        Use ``SETTINGS mutations_sync = 2`` on ALTER ... DELETE to wait for completion."""
        sql_guard.check_write(sql)
        return self._conn().command(sql, parameters=params)

    def ping(self) -> bool:
        """Return True when the server answers; False on connection failure."""
        try:
            return bool(self._conn().ping())
        except Exception as exc:  # noqa: BLE001 - connection errors vary by driver; logged
            logger.warning("ClickHouse ping failed: %s", exc)
            return False

    def close(self) -> None:
        if self._client is not None:
            self._client.close()
            self._client = None

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()
