from app.mfapi import MfapiClient
from app.models import IngestionResult
from app.repository import MarketDataRepository


class IngestionService:
    def __init__(self, client: MfapiClient, repository: MarketDataRepository) -> None:
        self.client = client
        self.repository = repository

    async def ingest_scheme(self, scheme_code: int) -> IngestionResult:
        history = await self.client.fetch_nav_history(scheme_code)
        changed = await self.repository.upsert_fund_and_navs(
            history.scheme_code, history.scheme_name, history.navs
        )
        return IngestionResult(
            scheme_code=history.scheme_code,
            scheme_name=history.scheme_name,
            nav_records_received=len(history.navs),
            nav_records_upserted=changed,
        )
