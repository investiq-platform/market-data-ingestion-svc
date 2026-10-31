from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, HTTPException, Query, Request

from app.config import settings
from app.mfapi import MfapiClient
from app.models import FundSearchResult, HealthResponse, IngestionResult, SchemeNavHistory
from app.repository import MarketDataRepository
from app.service import IngestionService


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.mfapi = MfapiClient(settings.mfapi_base_url, settings.mfapi_timeout_seconds)
    app.state.ingestion = IngestionService(app.state.mfapi, MarketDataRepository(settings.database_url))
    yield
    await app.state.mfapi.close()


app = FastAPI(title="Market Data Ingestion Service", version="0.1.0", lifespan=lifespan)


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse()


@app.get("/funds/search", response_model=list[FundSearchResult])
async def search_funds(request: Request, q: str = Query(min_length=2)) -> list[FundSearchResult]:
    try:
        return await request.app.state.mfapi.search_schemes(q)
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail="MFAPI search is unavailable") from exc


@app.get("/funds/{scheme_code}/navs", response_model=SchemeNavHistory)
async def nav_history(request: Request, scheme_code: int) -> SchemeNavHistory:
    try:
        return await request.app.state.mfapi.fetch_nav_history(scheme_code)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail="Scheme was not found") from exc
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail="MFAPI is unavailable") from exc


@app.post("/funds/{scheme_code}/ingest", response_model=IngestionResult)
async def ingest(request: Request, scheme_code: int) -> IngestionResult:
    try:
        return await request.app.state.ingestion.ingest_scheme(scheme_code)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail="Scheme was not found") from exc
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail="MFAPI is unavailable") from exc


@app.get("/funds/{scheme_code}/stored-navs", response_model=SchemeNavHistory)
async def stored_nav_history(request: Request, scheme_code: int, limit: int = Query(default=100, ge=1, le=500)) -> SchemeNavHistory:
    try:
        name, navs = await request.app.state.ingestion.repository.stored_navs(scheme_code, limit)
        return SchemeNavHistory(scheme_code=scheme_code, scheme_name=name, navs=navs)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail="Fund has not been ingested") from exc
