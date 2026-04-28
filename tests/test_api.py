"""Automatické testy API: validují endpointy, filtry a základní pravidla."""

from datetime import date

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.session import get_db
from app.main import app
from app.models.resource import Audience, Base, Keyword, Persona, Resource, Stage, Task


@pytest.fixture()
def client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )
    TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, class_=Session)
    Base.metadata.create_all(bind=engine)

    with TestingSessionLocal() as db:
        db.add_all(
            [
                Audience(code="DMO"),
                Audience(code="SME"),
                Audience(code="Public authority"),
                Audience(code="Data/tech provider"),
                Task(code="T1"),
                Task(code="T2"),
                Task(code="T3"),
                Task(code="T4"),
                Task(code="T5"),
                Stage(code="Explore"),
                Stage(code="Prepare"),
                Stage(code="Pilot"),
                Stage(code="Scale"),
                Persona(code="DMO"),
                Persona(code="SME"),
                Persona(code="Public authority"),
                Persona(code="Tech provider"),
            ]
        )
        db.add_all([Keyword(keyword="etds"), Keyword(keyword="governance")])
        db.commit()

        seed = Resource(
            resource_id="FAC-R-0001",
            title="Blueprint and Roadmap",
            url="https://www.tourismdataspace-csa.eu/",
            short_description="Seed description",
            resource_type="Blueprint",
            effort_level="deep dive",
            practicality_level="Background (with strong Implementation pointers via links)",
            language="EN",
            topic_area="Interoperability",
            recommended_rank=1,
            featured_m6=True,
            quality_note="note",
            source_owner_org="org",
            source_year_or_last_update="2023-12",
            access_conditions="Open",
            contributor_partner="DIHT4.0",
            review_status="Proposed",
            review_due_date=date(2026, 12, 31),
            last_checked_date=date.today(),
            editor_notes="",
        )
        seed.audience = db.execute(select(Audience).where(Audience.code.in_(["DMO", "SME"]))).scalars().all()
        seed.mapped_tasks = db.execute(select(Task).where(Task.code.in_(["T5"]))).scalars().all()
        seed.mapped_stages = db.execute(select(Stage).where(Stage.code.in_(["Prepare"]))).scalars().all()
        seed.mapped_personas = db.execute(select(Persona).where(Persona.code.in_(["DMO"]))).scalars().all()
        seed.keywords_tags = db.execute(select(Keyword).where(Keyword.keyword.in_(["etds"]))).scalars().all()
        db.add(seed)
        db.commit()

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def _payload(resource_id: str) -> dict:
    return {
        "resource_id": resource_id,
        "title": "New Resource",
        "url": "https://example.org/resource",
        "short_description": "Short text",
        "resource_type": "Guide",
        "audience": ["DMO", "SME"],
        "mapped_tasks": ["T1", "T2"],
        "mapped_stages": ["Explore"],
        "mapped_personas": ["DMO"],
        "effort_level": "medium",
        "practicality_level": "Implementation",
        "language": "EN",
        "keywords_tags": ["etds", "newtag"],
        "topic_area": "Interoperability",
        "recommended_rank": 2,
        "featured_m6": False,
        "quality_note": "Quality note",
        "source_owner_org": "Owner",
        "source_year_or_last_update": "2026-01",
        "access_conditions": "Open",
        "contributor_partner": "DIHT4.0",
        "review_status": "Proposed",
        "review_due_date": "2026-12-31",
        "last_checked_date": "2026-04-09",
        "editor_notes": "",
    }


def test_health(client: TestClient):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_ai_enrich_shape(client: TestClient):
    response = client.post("/ai/enrich", json={"url": "https://www.tourismdataspace-csa.eu/"})
    assert response.status_code == 200
    data = response.json()
    assert "title" in data
    assert "short_description" in data
    assert "keywords_tags" in data
    assert "mapped_tasks" in data
    assert "audience" in data


def test_get_resources_filters(client: TestClient):
    response = client.get("/resources?mapped_tasks=T5&mapped_stages=Prepare&keywords_tags=etds")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["resource_id"] == "FAC-R-0001"


def test_get_resources_fulltext_matches_text_fields(client: TestClient):
    response = client.get("/resources?q=roadmap")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["resource_id"] == "FAC-R-0001"


def test_get_resources_fulltext_matches_keywords(client: TestClient):
    response = client.get("/resources?q=etds")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["resource_id"] == "FAC-R-0001"


def test_get_resources_fulltext_combines_with_structured_filters(client: TestClient):
    response = client.get("/resources?q=seed&mapped_tasks=T5&mapped_stages=Prepare")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["resource_id"] == "FAC-R-0001"

    miss_response = client.get("/resources?q=seed&mapped_tasks=T5&mapped_stages=Scale")
    assert miss_response.status_code == 200
    assert miss_response.json() == []


def test_create_and_update_resource(client: TestClient):
    create_response = client.post("/resources", json=_payload("FAC-R-0002"))
    assert create_response.status_code == 201
    assert create_response.json()["resource_id"] == "FAC-R-0002"

    updated = _payload("FAC-R-0002")
    updated["title"] = "Updated Resource"
    updated["mapped_tasks"] = ["T3"]
    update_response = client.put("/resources/FAC-R-0002", json=updated)
    assert update_response.status_code == 200
    assert update_response.json()["title"] == "Updated Resource"
    assert update_response.json()["mapped_tasks"] == ["T3"]


def test_enum_validation_error(client: TestClient):
    bad = _payload("FAC-R-0003")
    bad["resource_type"] = "UnknownType"
    response = client.post("/resources", json=bad)
    assert response.status_code == 422


def test_ai_enrich_does_not_persist(client: TestClient):
    before = client.get("/resources")
    assert before.status_code == 200
    before_count = len(before.json())

    enrich = client.post("/ai/enrich", json={"url": "https://example.org"})
    assert enrich.status_code == 200

    after = client.get("/resources")
    assert after.status_code == 200
    assert len(after.json()) == before_count
