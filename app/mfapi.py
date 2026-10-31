from datetime import datetime

import httpx

from app.models import FundSearchResult, NavRecord, SchemeNavHistory


class MfapiClient:
    """Small typed client for the public MFAPI endpoints."""

    def __init__(self, base_url: str, timeout_seconds: float = 15.0) -> None:
        self._client = httpx.AsyncClient(base_url=base_url.rstrip("/"), timeout=timeout_seconds)

    async def close(self) -> None:
        await self._client.aclose()

    async def search_schemes(self, query: str) -> list[FundSearchResult]:
        response = await self._client.get("/mf/search", params={"q": query})
        response.raise_for_status()
        return [FundSearchResult.model_validate(item) for item in response.json()]

    async def fetch_nav_history(self, scheme_code: int) -> SchemeNavHistory:
        response = await self._client.get(f"/mf/{scheme_code}")
        response.raise_for_status()
        payload = response.json()
        metadata = payload["meta"]
        navs = [
            NavRecord(
                nav_date=datetime.strptime(item["date"], "%d-%m-%Y").date(),
                nav=float(item["nav"]),
            )
            for item in payload["data"]
        ]
        return SchemeNavHistory(
            scheme_code=int(metadata["scheme_code"]),
            scheme_name=metadata["scheme_name"],
            navs=navs,
        )
