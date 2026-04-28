"""API pro správu resource karet: list, detail, create, update a filtrace."""

from collections.abc import Sequence
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import Select, or_, select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.resource import Audience, Keyword, Persona, Resource, Stage, Task
from app.schemas.resource import (
    ResourceCardCreate,
    ResourceCardDraftCreate,
    ResourceCardOut,
    ResourceCardSummary,
    ResourceCardUpdate,
    ResourceEnrichCommand,
)
from app.services.enrichment import enrich_from_url

router = APIRouter(prefix="/resources", tags=["resources"])


def _to_resource_card(resource: Resource) -> ResourceCardOut:
    return ResourceCardOut(
        resource_id=resource.resource_id,
        title=resource.title,
        url=resource.url,
        short_description=resource.short_description,
        resource_type=resource.resource_type,
        audience=[a.code for a in resource.audience],
        mapped_tasks=[t.code for t in resource.mapped_tasks],
        mapped_stages=[s.code for s in resource.mapped_stages],
        mapped_personas=[p.code for p in resource.mapped_personas],
        effort_level=resource.effort_level,
        practicality_level=resource.practicality_level,
        language=resource.language,
        keywords_tags=[k.keyword for k in resource.keywords_tags],
        topic_area=resource.topic_area,
        recommended_rank=resource.recommended_rank,
        featured_m6=resource.featured_m6,
        quality_note=resource.quality_note,
        source_owner_org=resource.source_owner_org,
        source_year_or_last_update=resource.source_year_or_last_update,
        access_conditions=resource.access_conditions,
        contributor_partner=resource.contributor_partner,
        review_status=resource.review_status,
        review_due_date=resource.review_due_date,
        last_checked_date=resource.last_checked_date,
        editor_notes=resource.editor_notes,
    )


def _to_resource_summary(resource: Resource) -> ResourceCardSummary:
    return ResourceCardSummary(
        resource_id=resource.resource_id,
        title=resource.title,
        url=resource.url,
        short_description=resource.short_description,
    )


def _load_codes(db: Session, model, codes: Sequence[str], field_name: str):
    rows = db.execute(select(model).where(model.code.in_(codes))).scalars().all()
    found = {row.code for row in rows}
    missing = sorted(set(codes) - found)
    if missing:
        raise HTTPException(status_code=400, detail=f"Unknown {field_name}: {missing}")
    return rows


def _load_keywords(db: Session, keywords: Sequence[str]):
    existing = db.execute(select(Keyword).where(Keyword.keyword.in_(keywords))).scalars().all()
    found = {row.keyword for row in existing}
    new_keywords = [Keyword(keyword=k) for k in keywords if k not in found]
    if new_keywords:
        db.add_all(new_keywords)
        db.flush()
        existing.extend(new_keywords)
    return existing


def _apply_payload(resource: Resource, payload: ResourceCardCreate | ResourceCardUpdate, db: Session) -> None:
    resource.title = payload.title
    resource.url = str(payload.url)
    resource.short_description = payload.short_description
    resource.resource_type = payload.resource_type
    resource.effort_level = payload.effort_level
    resource.practicality_level = payload.practicality_level
    resource.language = payload.language
    resource.topic_area = payload.topic_area
    resource.recommended_rank = payload.recommended_rank
    resource.featured_m6 = payload.featured_m6
    resource.quality_note = payload.quality_note
    resource.source_owner_org = payload.source_owner_org
    resource.source_year_or_last_update = payload.source_year_or_last_update
    resource.access_conditions = payload.access_conditions
    resource.contributor_partner = payload.contributor_partner
    resource.review_status = payload.review_status
    resource.review_due_date = payload.review_due_date
    resource.last_checked_date = payload.last_checked_date
    resource.editor_notes = payload.editor_notes
    resource.audience = _load_codes(db, Audience, payload.audience, "audience")
    resource.mapped_tasks = _load_codes(db, Task, payload.mapped_tasks, "mapped_tasks")
    resource.mapped_stages = _load_codes(db, Stage, payload.mapped_stages, "mapped_stages")
    resource.mapped_personas = _load_codes(db, Persona, payload.mapped_personas, "mapped_personas")
    resource.keywords_tags = _load_keywords(db, payload.keywords_tags)


@router.get("", response_model=list[ResourceCardSummary])
def list_resources(
    q: str | None = Query(default=None, min_length=1),
    mapped_tasks: list[str] = Query(default=[]),
    mapped_stages: list[str] = Query(default=[]),
    mapped_personas: list[str] = Query(default=[]),
    keywords_tags: list[str] = Query(default=[]),
    db: Session = Depends(get_db),
):
    stmt: Select = select(Resource).distinct()
    if q:
        search_term = f"%{q.strip()}%"
        stmt = stmt.outerjoin(Resource.keywords_tags).where(
            or_(
                Resource.resource_id.ilike(search_term),
                Resource.title.ilike(search_term),
                Resource.short_description.ilike(search_term),
                Resource.topic_area.ilike(search_term),
                Keyword.keyword.ilike(search_term),
            )
        )
    if mapped_tasks:
        stmt = stmt.join(Resource.mapped_tasks).where(Task.code.in_(mapped_tasks))
    if mapped_stages:
        stmt = stmt.join(Resource.mapped_stages).where(Stage.code.in_(mapped_stages))
    if mapped_personas:
        stmt = stmt.join(Resource.mapped_personas).where(Persona.code.in_(mapped_personas))
    if keywords_tags:
        stmt = stmt.join(Resource.keywords_tags).where(Keyword.keyword.in_(keywords_tags))

    resources = db.execute(stmt).scalars().all()
    return [_to_resource_summary(r) for r in resources]


@router.get("/{resource_id}", response_model=ResourceCardOut)
def get_resource(resource_id: str, db: Session = Depends(get_db)):
    resource = db.get(Resource, resource_id)
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    return _to_resource_card(resource)


@router.post("", response_model=ResourceCardOut, status_code=201)
def create_resource(payload: ResourceCardCreate, db: Session = Depends(get_db)):
    if db.get(Resource, payload.resource_id):
        raise HTTPException(status_code=409, detail="resource_id already exists")

    resource = Resource(resource_id=payload.resource_id)
    _apply_payload(resource, payload, db)
    db.add(resource)
    db.commit()
    db.refresh(resource)
    return _to_resource_card(resource)


@router.post("/draft", response_model=ResourceCardOut, status_code=201)
def create_draft_resource(payload: ResourceCardDraftCreate, db: Session = Depends(get_db)):
    if db.get(Resource, payload.resource_id):
        raise HTTPException(status_code=409, detail="resource_id already exists")

    resource = Resource(
        resource_id=payload.resource_id,
        title=payload.title,
        url=str(payload.url),
        short_description="Draft card created from minimal input. Run AI enrichment to expand fields.",
        resource_type="Guide",
        effort_level="quick win",
        practicality_level="Background",
        language=payload.language,
        topic_area="General",
        recommended_rank=None,
        featured_m6=False,
        quality_note="Draft - pending editorial review.",
        source_owner_org="Unknown",
        source_year_or_last_update=str(date.today().year),
        access_conditions="Open",
        contributor_partner="Unknown",
        review_status="Proposed",
        review_due_date=date.today(),
        last_checked_date=date.today(),
        editor_notes="Draft created via minimal UI flow.",
    )
    db.add(resource)
    db.commit()
    db.refresh(resource)
    return _to_resource_card(resource)


@router.post("/{resource_id}/enrich", response_model=ResourceCardOut)
def enrich_resource(resource_id: str, payload: ResourceEnrichCommand, db: Session = Depends(get_db)):
    resource = db.get(Resource, resource_id)
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")

    target_url = str(payload.url) if payload.url else resource.url
    enrichment = enrich_from_url(url=target_url, title=resource.title)

    if payload.url:
        resource.url = target_url
    if enrichment.title:
        resource.title = enrichment.title
    if enrichment.short_description:
        resource.short_description = enrichment.short_description
    if enrichment.resource_type:
        resource.resource_type = enrichment.resource_type
    if enrichment.effort_level:
        resource.effort_level = enrichment.effort_level
    if enrichment.practicality_level:
        resource.practicality_level = enrichment.practicality_level
    if enrichment.topic_area:
        resource.topic_area = enrichment.topic_area
    if enrichment.source_owner_org:
        resource.source_owner_org = enrichment.source_owner_org
    if enrichment.source_year_or_last_update:
        resource.source_year_or_last_update = enrichment.source_year_or_last_update
    if enrichment.access_conditions:
        resource.access_conditions = enrichment.access_conditions
    if enrichment.contributor_partner:
        resource.contributor_partner = enrichment.contributor_partner
    if enrichment.quality_note:
        resource.quality_note = enrichment.quality_note
    if enrichment.editor_notes:
        resource.editor_notes = enrichment.editor_notes
    if enrichment.language:
        resource.language = enrichment.language
    if enrichment.mapped_tasks:
        resource.mapped_tasks = _load_codes(db, Task, enrichment.mapped_tasks, "mapped_tasks")
    if enrichment.mapped_stages:
        resource.mapped_stages = _load_codes(db, Stage, enrichment.mapped_stages, "mapped_stages")
    if enrichment.mapped_personas:
        resource.mapped_personas = _load_codes(db, Persona, enrichment.mapped_personas, "mapped_personas")
    if enrichment.audience:
        resource.audience = _load_codes(db, Audience, enrichment.audience, "audience")
    if enrichment.keywords_tags:
        resource.keywords_tags = _load_keywords(db, enrichment.keywords_tags)

    resource.last_checked_date = date.today()
    db.commit()
    db.refresh(resource)
    return _to_resource_card(resource)


@router.put("/{resource_id}", response_model=ResourceCardOut)
def update_resource(resource_id: str, payload: ResourceCardUpdate, db: Session = Depends(get_db)):
    resource = db.get(Resource, resource_id)
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")

    if payload.resource_id != resource_id:
        raise HTTPException(status_code=400, detail="resource_id in path and body must match")

    _apply_payload(resource, payload, db)
    db.commit()
    db.refresh(resource)
    return _to_resource_card(resource)


@router.delete("/{resource_id}", status_code=204)
def delete_resource(resource_id: str, db: Session = Depends(get_db)):
    resource = db.get(Resource, resource_id)
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")

    db.delete(resource)
    db.commit()
    return None
