"""Pomocný skript: aplikuje SQL migraci do PostgreSQL databáze."""

import os
from pathlib import Path

import psycopg2


def main() -> None:
    database_url = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/resource_catalog",
    )
    migration_path = Path(__file__).resolve().parents[1] / "db" / "migrations" / "001_init.sql"

    sql = migration_path.read_text(encoding="utf-8")
    with psycopg2.connect(database_url) as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
        conn.commit()

    print(f"Migration applied: {migration_path}")


if __name__ == "__main__":
    main()
