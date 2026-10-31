from datetime import date

from pydantic import AliasChoices, BaseModel, ConfigDict, Field


class FundSearchResult(BaseModel):
    scheme_code: int = Field(validation_alias=AliasChoices("scheme_code", "schemeCode"))
    scheme_name: str = Field(validation_alias=AliasChoices("scheme_name", "schemeName"))


class NavRecord(BaseModel):
    nav_date: date
    nav: float = Field(gt=0)


class SchemeNavHistory(BaseModel):
    scheme_code: int
    scheme_name: str
    navs: list[NavRecord]


class IngestionResult(BaseModel):
    scheme_code: int
    scheme_name: str
    nav_records_received: int
    nav_records_upserted: int


class HealthResponse(BaseModel):
    model_config = ConfigDict(frozen=True)
    status: str = "ok"
