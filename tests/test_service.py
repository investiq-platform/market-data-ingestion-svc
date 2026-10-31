from datetime import date

import pytest

from app.models import NavRecord, SchemeNavHistory
from app.service import IngestionService


class FakeClient:
    async def fetch_nav_history(self, scheme_code: int) -> SchemeNavHistory:
        return SchemeNavHistory(scheme_code=scheme_code, scheme_name="Test Fund", navs=[NavRecord(nav_date=date(2026, 10, 30), nav=10.5)])


class FakeRepository:
    def __init__(self) -> None:
        self.seen: set[tuple[int, date]] = set()

    async def upsert_fund_and_navs(self, scheme_code: int, scheme_name: str, navs: list[NavRecord]) -> int:
        changed = 0
        for nav in navs:
            key = (scheme_code, nav.nav_date)
            if key not in self.seen:
                self.seen.add(key)
                changed += 1
        return changed


@pytest.mark.asyncio
async def test_repeat_ingestion_reports_no_new_navs() -> None:
    service = IngestionService(FakeClient(), FakeRepository())
    assert (await service.ingest_scheme(120503)).nav_records_upserted == 1
    assert (await service.ingest_scheme(120503)).nav_records_upserted == 0
