"""Pomocný skript: rychle ověří, že hlavní API endpointy fungují."""

import json
import os
from urllib.parse import quote_plus
from urllib.request import urlopen


BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:8000")


def get(path: str):
    with urlopen(f"{BASE_URL}{path}") as response:
        return json.loads(response.read().decode("utf-8"))


def post(path: str, payload: dict):
    import urllib.request

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"{BASE_URL}{path}",
        data=data,
        method="POST",
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode("utf-8"))


def main() -> None:
    health = get("/health")
    assert health["status"] == "ok", "Health check failed"

    resources = get("/resources")
    assert isinstance(resources, list), "GET /resources must return a list"
    assert any(r["resource_id"] == "FAC-R-0001" for r in resources), "Seed FAC-R-0001 not found"

    seed = get(f"/resources/{quote_plus('FAC-R-0001')}")
    assert seed["resource_id"] == "FAC-R-0001", "GET /resources/{id} returned wrong id"

    enriched = post("/ai/enrich", {"url": "https://www.tourismdataspace-csa.eu/"})
    for key in ["title", "short_description", "keywords_tags", "mapped_tasks", "audience"]:
        assert key in enriched, f"Missing key in /ai/enrich response: {key}"

    print("Smoke test passed.")


if __name__ == "__main__":
    main()
