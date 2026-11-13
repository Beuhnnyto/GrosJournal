"""Stockage brut (fichiers) et propre (PostgreSQL)."""

import json
from datetime import datetime
from pathlib import Path

import psycopg

from gazette.sources import Source

SCHEMA = """
CREATE TABLE IF NOT EXISTS articles (
    id           text PRIMARY KEY,
    source       text NOT NULL,
    source_type  text NOT NULL,
    region       text NOT NULL,
    title        text NOT NULL,
    summary      text NOT NULL DEFAULT '',
    url          text NOT NULL,
    published_at timestamptz,
    fetched_at   timestamptz NOT NULL,
    inserted_at  timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS articles_published_at_idx ON articles (published_at);
CREATE INDEX IF NOT EXISTS articles_source_idx ON articles (source);
"""

INSERT = """
INSERT INTO articles
    (id, source, source_type, region, title, summary, url, published_at, fetched_at)
VALUES
    (%(id)s, %(source)s, %(source_type)s, %(region)s, %(title)s, %(summary)s, %(url)s,
     %(published_at)s, %(fetched_at)s)
ON CONFLICT (id) DO NOTHING
"""


def write_raw(
    data_dir: Path, source: Source, fetched_at: datetime, content: bytes, articles: list[dict]
) -> Path:
    """Écrit le flux tel que reçu (.xml) et les articles parsés (.json) ; renvoie le .json."""
    day_dir = data_dir / "raw" / fetched_at.strftime("%Y-%m-%d")
    day_dir.mkdir(parents=True, exist_ok=True)
    stem = f"{source.slug}-{fetched_at.strftime('%H%M%S')}"
    (day_dir / f"{stem}.xml").write_bytes(content)
    json_path = day_dir / f"{stem}.json"
    json_path.write_text(json.dumps(articles, ensure_ascii=False, indent=2), encoding="utf-8")
    return json_path


def ensure_schema(conn: psycopg.Connection) -> None:
    conn.execute(SCHEMA)
    conn.commit()


def insert_articles(conn: psycopg.Connection, articles: list[dict]) -> int:
    """Insère les nouveaux articles ; renvoie le nombre de lignes réellement ajoutées."""
    inserted = 0
    with conn.cursor() as cur:
        for article in articles:
            cur.execute(INSERT, article)
            inserted += cur.rowcount
    conn.commit()
    return inserted
