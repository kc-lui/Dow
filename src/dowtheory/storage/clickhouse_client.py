"""Guarded ClickHouse client: writes only to database ``dow``, never DROP/TRUNCATE."""

from __future__ import annotations

import logging
import os
import re
from typing import Any, Self

import pandas as pd

logger = logging.getLogger(__name__)

ALLOWED_DATABASE = "dow"
INSERT_CHUNK_ROWS = 1000
_FORBIDDEN_SQL = re.compile(r"\b(DROP|TRUNCATE)\b", re.IGNORECASE)


class UnsafeSQLError(RuntimeError):
    """Raised when a statement or target violates the project's write-scope rules."""


def _guard_sql(sql: str) -> None:
    if _FORBIDDEN_SQL.search(sql):
        raise UnsafeSQLError(f"DROP/TRUNCATE is forbidden: {sql[:80]!r}")


class ClickHouseClient:
    """Thin env-driven wrapper around clickhouse-connect. Connection is opened lazily."""

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
            raise UnsafeSQLError(
                f"Database must be '{ALLOWED_DATABASE}', got '{self.database}'"
            )
        self._params: dict[str, Any] = {
            "host": host or os.getenv("CLICKHOUSE_HOST", "localhost"),
            "port": int(port or os.getenv("CLICKHOUSE_PORT", "8123")),
            "username": user or os.getenv("CLICKHOUSE_USER", "trading_user"),
            "password": password or os.getenv("CLICKHOUSE_PASSWORD", "trading_secret"),
            "database": self.database,
        }
        self._client: Any = None

    def _conn(self) -> Any:
        if self._client is None:
            import clickhouse_connect

            self._client = clickhouse_connect.get_client(**self._params)
        return self._client

    def query_df(self, sql: str, params: dict[str, Any] | None = None) -> pd.DataFrame:
        """Run a read query and return a DataFrame."""
        _guard_sql(sql)
        return self._conn().query_df(sql, parameters=params)

    def insert_df(self, table: str, df: pd.DataFrame) -> int:
        """Insert ``df`` into ``dow.<table>``; returns the number of rows sent."""
        if not table.startswith(f"{ALLOWED_DATABASE}."):
            raise UnsafeSQLError(f"Insert target must start with 'dow.', got '{table}'")
        if df.empty:
            raise ValueError(f"Refusing to insert an empty frame into {table}")
        # Chunked: a single block may not span more than max_partitions_per_insert_block (100).
        for lo in range(0, len(df), INSERT_CHUNK_ROWS):
            self._conn().insert_df(table, df.iloc[lo : lo + INSERT_CHUNK_ROWS])
        return len(df)

    def command(self, sql: str, params: dict[str, Any] | None = None) -> Any:
        """Run a DDL/DML statement (ALTER ... DELETE allowed; DROP/TRUNCATE refused)."""
        _guard_sql(sql)
        return self._conn().command(sql, parameters=params)

    def ping(self) -> bool:
        """Return True when the server answers; False on connection failure."""
        try:
            return bool(self._conn().ping())
        except Exception as exc:  # noqa: BLE001 - connection errors vary by driver; reported, not hidden
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
