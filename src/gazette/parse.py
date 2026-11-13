"""Transforme un flux RSS/Atom en articles normalisés."""

import hashlib
import html
import re
from datetime import UTC, datetime
from html.parser import HTMLParser

import feedparser

from gazette.sources import Source

SUMMARY_MAX_CHARS = 300


class _TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        self.parts.append(data)


def html_to_text(value: str) -> str:
    extractor = _TextExtractor()
    extractor.feed(value)
    extractor.close()
    return re.sub(r"\s+", " ", html.unescape("".join(extractor.parts))).strip()


def truncate(text: str, max_chars: int = SUMMARY_MAX_CHARS) -> str:
    if len(text) <= max_chars:
        return text
    cut = text[: max_chars - 1].rsplit(" ", 1)[0]
    return cut.rstrip(" ,;:.") + "…"


def article_id(url: str) -> str:
    return hashlib.sha256(url.encode()).hexdigest()


def _published_at(entry: feedparser.FeedParserDict) -> datetime | None:
    # feedparser convertit déjà les dates en UTC (struct_time)
    parsed = entry.get("published_parsed") or entry.get("updated_parsed")
    if parsed is None:
        return None
    return datetime(*parsed[:6], tzinfo=UTC)


def parse_feed(content: bytes, source: Source, fetched_at: datetime) -> list[dict]:
    """Renvoie un dict par article. On ne garde jamais l'auteur (RGPD) ni le corps."""
    feed = feedparser.parse(content)
    if feed.bozo and not feed.entries:
        raise ValueError(f"Flux illisible pour {source.name}: {feed.bozo_exception}")

    articles = []
    for entry in feed.entries:
        url = (entry.get("link") or "").strip()
        title = html_to_text(entry.get("title") or "")
        if not url or not title:
            continue
        published_at = _published_at(entry)
        articles.append(
            {
                "id": article_id(url),
                "source": source.name,
                "source_type": source.type,
                "region": source.region,
                "title": title,
                "summary": truncate(html_to_text(entry.get("summary") or "")),
                "url": url,
                "published_at": published_at.isoformat() if published_at else None,
                "fetched_at": fetched_at.isoformat(),
            }
        )
    return articles
