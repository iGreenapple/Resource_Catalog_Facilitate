"""API endpoint pro AI enrichment z URL bez ukládání do databáze."""

from fastapi import APIRouter

from app.schemas.resource import EnrichRequest, EnrichResponse
from app.services.enrichment import enrich_from_url

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/enrich", response_model=EnrichResponse)
def enrich(payload: EnrichRequest):
    return enrich_from_url(url=str(payload.url), title=payload.title)
