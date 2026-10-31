from collections.abc import Iterable

import psycopg
from psycopg.rows import dict_row

from app.models import NavRecord


class MarketDataRepository:
    def __init__(self, database_url: str) -> None:
        self.database_url = database_url

    async def upsert_fund_and_navs(
        self, scheme_code: int, scheme_name: str, navs: Iterable[NavRecord]
    ) -> int:
        rows = [(scheme_code, nav.nav_date, nav.nav) for nav in navs]
        if not rows:
            return 0
        async with await psycopg.AsyncConnection.connect(self.database_url) as connection:
            async with connection.cursor(row_factory=dict_row) as cursor:
                await cursor.execute(
                    """
                    INSERT INTO mutual_funds (scheme_code, scheme_name)
                    VALUES (%s, %s)
                    ON CONFLICT (scheme_code) DO UPDATE
                    SET scheme_name = EXCLUDED.scheme_name, updated_at = now()
                    """,
                    (scheme_code, scheme_name),
                )
                await cursor.executemany(
                    """
                    INSERT INTO nav_history (scheme_code, nav_date, nav)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (scheme_code, nav_date) DO UPDATE
                    SET nav = EXCLUDED.nav, updated_at = now()
                    WHERE nav_history.nav IS DISTINCT FROM EXCLUDED.nav
                    """,
                    rows,
                )
                # rowcount from executemany is the count inserted/changed by this batch.
                changed = cursor.rowcount
            await connection.commit()
        return max(changed, 0)

    async def stored_navs(self, scheme_code: int, limit: int) -> tuple[str, list[NavRecord]]:
        async with await psycopg.AsyncConnection.connect(self.database_url) as connection:
            async with connection.cursor(row_factory=dict_row) as cursor:
                await cursor.execute("SELECT scheme_name FROM mutual_funds WHERE scheme_code = %s", (scheme_code,))
                fund = await cursor.fetchone()
                if fund is None:
                    raise LookupError("Fund has not been ingested")
                await cursor.execute(
                    "SELECT nav_date, nav FROM nav_history WHERE scheme_code = %s ORDER BY nav_date DESC LIMIT %s",
                    (scheme_code, limit),
                )
                rows = await cursor.fetchall()
        return fund["scheme_name"], [NavRecord(nav_date=row["nav_date"], nav=float(row["nav"])) for row in rows]
