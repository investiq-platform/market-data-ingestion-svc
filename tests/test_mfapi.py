import httpx
import pytest

from app.mfapi import MfapiClient


@pytest.mark.asyncio
async def test_parses_search_and_nav_history() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/mf/search":
            return httpx.Response(200, json=[{"schemeCode": 120503, "schemeName": "Axis Bluechip Fund"}])
        return httpx.Response(200, json={"meta": {"scheme_code": 120503, "scheme_name": "Axis Bluechip Fund"}, "data": [{"date": "30-10-2026", "nav": "74.25"}]})

    client = MfapiClient("https://example.test")
    await client._client.aclose()
    client._client = httpx.AsyncClient(base_url="https://example.test", transport=httpx.MockTransport(handler))
    assert (await client.search_schemes("axis"))[0].scheme_code == 120503
    history = await client.fetch_nav_history(120503)
    assert history.navs[0].nav == 74.25
    await client.close()
