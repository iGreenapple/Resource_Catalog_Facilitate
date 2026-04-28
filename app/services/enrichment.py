"""Gemini-based enrichment for Resource Card draft data."""

import json
import os
import re
from datetime import date
from html import unescape
from urllib.parse import urlparse

import httpx

from app.schemas.enums import (
    ACCESS_CONDITIONS_VALUES,
    AUDIENCE_VALUES,
    EFFORT_LEVEL_VALUES,
    PERSONA_VALUES,
    PRACTICALITY_LEVEL_VALUES,
    RESOURCE_TYPE_VALUES,
    STAGE_VALUES,
    TASK_VALUES,
)
from app.schemas.resource import EnrichResponse

GEMINI_API_URL = os.getenv(
    "GEMINI_API_URL", 
    "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
)
DEFAULT_GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
MAX_PAGE_TEXT_CHARS = 15000


def _normalize_list(values: object, allowed_values: set[str]) -> list[str]:
    if not isinstance(values, list):
        return []
    normalized: list[str] = []
    seen: set[str] = set()
    for value in values:
        if isinstance(value, str) and value in allowed_values and value not in seen:
            normalized.append(value)
            seen.add(value)
    return normalized


def _safe_text(value: object, max_len: int = 600) -> str | None:
    if not isinstance(value, str):
        return None
    cleaned = value.strip()
    if not cleaned:
        return None
    return cleaned[:max_len]


def _extract_json_block(text: str) -> dict:
    fenced_match = re.search(r"```json\s*(\{.*?\})\s*```", text, flags=re.S | re.I)
    if fenced_match:
        return json.loads(fenced_match.group(1))

    plain_match = re.search(r"(\{.*\})", text, flags=re.S)
    if plain_match:
        return json.loads(plain_match.group(1))

    raise ValueError("No JSON object found in Gemini response.")


def _html_to_text(html: str) -> str:
    without_script = re.sub(r"<script\b[^<]*(?:(?!</script>)<[^<]*)*</script>", " ", html, flags=re.I | re.S)
    without_style = re.sub(r"<style\b[^<]*(?:(?!</style>)<[^<]*)*</style>", " ", without_script, flags=re.I | re.S)
    without_tags = re.sub(r"<[^>]+>", " ", without_style)
    text = unescape(without_tags)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:MAX_PAGE_TEXT_CHARS]


def _download_page_text(url: str) -> str:
    headers = {
        "User-Agent": "FACILITATE-Resource-Catalog/1.0 (+AI enrichment)",
        "Accept": "text/html,application/xhtml+xml",
    }
    with httpx.Client(timeout=12.0, follow_redirects=True) as client:
        response = client.get(url, headers=headers)
        response.raise_for_status()
        content_type = response.headers.get("content-type", "")
        if "text/html" not in content_type:
            return ""
        return _html_to_text(response.text)


def _fallback_from_url(url: str, title: str | None) -> EnrichResponse:
    parsed = urlparse(url)
    host = parsed.netloc.replace("www.", "")
    guessed_keywords = [part for part in host.split(".") if part]
    return EnrichResponse(
        title=title or f"Resource from {host}",
        short_description=f"Draft enrichment for {url}. Please review before saving.",
        keywords_tags=sorted(set(guessed_keywords))[:10],
        source_year_or_last_update=str(date.today().year),
        access_conditions="Open",
    )


def _build_prompt(url: str, title: str | None, page_text: str) -> str:
    return f"""
You are a strict data extraction assistant for FACILITATE Resource Cards.
Output ONLY valid JSON. Do not include markdown or explanations.
If a value is unknown, use null (or [] for arrays). Never invent facts.

INPUT:
- url: {url}
- provided_title: {title or ""}
- page_text: {page_text}

ALLOWED ENUM VALUES:
- resource_type: {sorted(RESOURCE_TYPE_VALUES)}
- audience: {sorted(AUDIENCE_VALUES)}
- mapped_tasks: {sorted(TASK_VALUES)}
- mapped_stages: {sorted(STAGE_VALUES)}
- mapped_personas: {sorted(PERSONA_VALUES)}
- effort_level: {sorted(EFFORT_LEVEL_VALUES)}
- practicality_level: {sorted(PRACTICALITY_LEVEL_VALUES)}
- access_conditions: {sorted(ACCESS_CONDITIONS_VALUES)}

Return JSON with exactly these keys:
{{
  "title": string|null,
  "short_description": string|null,
  "resource_type": string|null,
  "audience": string[],
  "mapped_tasks": string[],
  "mapped_stages": string[],
  "mapped_personas": string[],
  "effort_level": string|null,
  "practicality_level": string|null,
  "language": string|null,
  "keywords_tags": string[],
  "topic_area": string|null,
  "quality_note": string|null,
  "source_owner_org": string|null,
  "source_year_or_last_update": string|null,
  "access_conditions": string|null,
  "contributor_partner": string|null,
  "editor_notes": string|null
}}
""".strip()


def _call_gemini(url: str, title: str | None, page_text: str) -> dict:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not set.")

    model = os.getenv("GEMINI_MODEL", DEFAULT_GEMINI_MODEL)
    endpoint = GEMINI_API_URL.format(model=model)
    prompt = _build_prompt(url=url, title=title, page_text=page_text)
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.1,
            "responseMimeType": "application/json",
        },
    }

    with httpx.Client(timeout=25.0) as client:
        response = client.post(
            endpoint,
            params={"key": api_key},
            json=payload,
            headers={"Content-Type": "application/json"},
        )
        response.raise_for_status()
        data = response.json()

    candidates = data.get("candidates", [])
    if not candidates:
        raise RuntimeError("Gemini returned no candidates.")

    parts = candidates[0].get("content", {}).get("parts", [])
    text_chunks = [p.get("text", "") for p in parts if isinstance(p, dict)]
    raw_text = "\n".join(chunk for chunk in text_chunks if chunk).strip()
    if not raw_text:
        raise RuntimeError("Gemini returned empty content.")

    return _extract_json_block(raw_text)


def enrich_from_url(url: str, title: str | None = None) -> EnrichResponse:
    try:
        page_text = _download_page_text(url)
        ai_payload = _call_gemini(url=url, title=title, page_text=page_text)
    except Exception:
        return _fallback_from_url(url, title=title)

    return EnrichResponse(
        title=_safe_text(ai_payload.get("title"), max_len=300),
        short_description=_safe_text(ai_payload.get("short_description"), max_len=1500),
        resource_type=_safe_text(ai_payload.get("resource_type"), max_len=100)
        if ai_payload.get("resource_type") in RESOURCE_TYPE_VALUES
        else None,
        audience=_normalize_list(ai_payload.get("audience"), AUDIENCE_VALUES),
        mapped_tasks=_normalize_list(ai_payload.get("mapped_tasks"), TASK_VALUES),
        mapped_stages=_normalize_list(ai_payload.get("mapped_stages"), STAGE_VALUES),
        mapped_personas=_normalize_list(ai_payload.get("mapped_personas"), PERSONA_VALUES),
        effort_level=_safe_text(ai_payload.get("effort_level"), max_len=100)
        if ai_payload.get("effort_level") in EFFORT_LEVEL_VALUES
        else None,
        practicality_level=_safe_text(ai_payload.get("practicality_level"), max_len=200)
        if ai_payload.get("practicality_level") in PRACTICALITY_LEVEL_VALUES
        else None,
        language=_safe_text(ai_payload.get("language"), max_len=20),
        keywords_tags=[
            kw.strip()[:80]
            for kw in ai_payload.get("keywords_tags", [])
            if isinstance(kw, str) and kw.strip()
        ][:15],
        topic_area=_safe_text(ai_payload.get("topic_area"), max_len=200),
        quality_note=_safe_text(ai_payload.get("quality_note"), max_len=600),
        source_owner_org=_safe_text(ai_payload.get("source_owner_org"), max_len=250),
        source_year_or_last_update=_safe_text(ai_payload.get("source_year_or_last_update"), max_len=20),
        access_conditions=_safe_text(ai_payload.get("access_conditions"), max_len=100)
        if ai_payload.get("access_conditions") in ACCESS_CONDITIONS_VALUES
        else None,
        contributor_partner=_safe_text(ai_payload.get("contributor_partner"), max_len=200),
        editor_notes=_safe_text(ai_payload.get("editor_notes"), max_len=1000),
    )
