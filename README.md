# FACILITATE Resource Catalogue MVP

MVP backend pro Resource Catalogue nad `FastAPI + PostgreSQL`, navržený striktně podle dohodnutého Resource Card schématu.

## Co je implementováno

- SQL migrace se normalizovaným modelem bez JSON blobů: `db/migrations/001_init.sql`
- M:N relace pro `audience`, `mapped_tasks`, `mapped_stages`, `mapped_personas`, `keywords_tags`
- API endpointy:
  - `GET /resources`
  - `GET /resources/{id}`
  - `POST /resources/draft` (vytvoření draft karty z minima dat)
  - `POST /resources/{id}/enrich` (rozšíření existující karty přes enrichment)
  - `POST /resources`
  - `PUT /resources/{id}`
  - `POST /ai/enrich` (bez persistence)
- AI enrichment běží přes Gemini API (`GEMINI_API_KEY`)
- Seed karta `FAC-R-0001` dle potvrzeného zadání

## Rychlé spuštění

1. Nainstaluj závislosti:
   - `pip install -r requirements.txt`
2. Vytvoř `.env` (např. kopie `.env.example`) a nastav:
   - `DATABASE_URL=...`
   - `GEMINI_API_KEY=...`
   - volitelně `GEMINI_MODEL=gemini-1.5-flash`
3. Připrav PostgreSQL databázi a nastav:
   - `DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/resource_catalog`
4. Spusť migraci:
   - `python scripts/migrate.py`
5. Spusť API:
   - `uvicorn app.main:app --reload`

## Automatizované ověření

- Po spuštění API můžeš pustit smoke test:
  - `python scripts/smoke_test.py`
- Smoke test ověřuje:
  - `/health`
  - `/resources` (včetně seed `FAC-R-0001`)
  - `/resources/{id}`
  - `/ai/enrich`

## Filtrace v GET /resources

- `q` - fulltextové vyhledávání přes `resource_id`, `title`, `short_description`, `topic_area`, `keywords_tags`
- `mapped_tasks` - opakovatelný query parametr
- `mapped_stages` - opakovatelný query parametr
- `mapped_personas` - opakovatelný query parametr
- `keywords_tags` - opakovatelný query parametr

Chování: OR uvnitř jednoho parametru, AND mezi různými parametry.

Příklad:
- `/resources?mapped_tasks=T5&mapped_tasks=T4&mapped_stages=Prepare&keywords_tags=etds`
- `/resources?q=roadmap&mapped_stages=Prepare`

## Draft enum hodnoty (MVP)

- `resource_type`: `Blueprint`, `Guide`, `Toolkit`, `Policy`, `Case study`, `Training`, `Dataset`, `Platform`
- `audience`: `DMO`, `SME`, `Public authority`, `Data/tech provider`
- `mapped_tasks`: `T1`, `T2`, `T3`, `T4`, `T5`
- `mapped_stages`: `Explore`, `Prepare`, `Pilot`, `Scale`
- `mapped_personas`: `DMO`, `SME`, `Public authority`, `Tech provider`
- `effort_level`: `quick win`, `medium`, `deep dive`
- `practicality_level`: `Background`, `Background (with strong Implementation pointers via links)`, `Implementation`, `Mixed`
- `access_conditions`: `Open`, `Registration`, `Paid`, `Restricted`
- `review_status`: `Proposed`, `Approved`, `Needs update`, `Archived`

## Poznámky k CMS (Directus)

- Directus je doporučen jako volitelný backoffice nad stejnou DB.
- Backend zůstává CMS-agnostický; žádná business logika není vázána na Directus.
