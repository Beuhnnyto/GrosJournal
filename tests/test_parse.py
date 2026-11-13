from datetime import UTC, datetime

import pytest

from gazette.parse import SUMMARY_MAX_CHARS, article_id, html_to_text, parse_feed, truncate
from gazette.sources import Source

FETCHED_AT = datetime(2026, 11, 13, 13, 37, tzinfo=UTC)
LE_MONDE = Source("Le Monde", "PQN", "National", "https://www.lemonde.fr/rss/une.xml")
OUEST_FRANCE = Source("Ouest-France", "PQR", "Bretagne", "https://www.ouest-france.fr/rss/une")

EXPECTED_KEYS = {
    "id",
    "source",
    "source_type",
    "region",
    "title",
    "summary",
    "url",
    "published_at",
    "fetched_at",
}


def test_parse_le_monde_fixture(fixtures_dir):
    articles = parse_feed((fixtures_dir / "le-monde-une.xml").read_bytes(), LE_MONDE, FETCHED_AT)

    assert len(articles) == 16
    first = articles[0]
    assert set(first) == EXPECTED_KEYS
    assert first["source"] == "Le Monde"
    assert first["source_type"] == "PQN"
    assert first["title"] == "Ce que l’on sait de la panne d’Outlook et de Microsoft 365"
    assert first["url"].startswith("https://www.lemonde.fr/pixels/article/2026/11/13/")
    assert first["id"] == article_id(first["url"])
    # 11:42:43 +0100 dans le flux -> normalisé en UTC
    assert first["published_at"] == "2026-11-13T10:42:43+00:00"
    assert first["fetched_at"] == FETCHED_AT.isoformat()


def test_parse_ouest_france_fixture(fixtures_dir):
    content = (fixtures_dir / "ouest-france-une.xml").read_bytes()
    articles = parse_feed(content, OUEST_FRANCE, FETCHED_AT)

    assert len(articles) == 10
    assert all(a["title"] and a["url"] and a["published_at"] for a in articles)
    assert all(len(a["summary"]) <= SUMMARY_MAX_CHARS for a in articles)
    assert len({a["id"] for a in articles}) == len(articles)


FEED_WITH_EDGE_CASES = b"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:dc="http://purl.org/dc/elements/1.1/">
  <channel>
    <title>Test</title>
    <item>
      <title>Titre &amp; <b>gras</b></title>
      <link> https://exemple.fr/a </link>
      <description>&lt;p&gt;Un &lt;a href="x"&gt;chap\xc3\xb4&lt;/a&gt;
        avec   espaces&lt;/p&gt;</description>
      <dc:creator>Jeanne Dupont</dc:creator>
    </item>
    <item>
      <title>Sans lien</title>
    </item>
    <item>
      <link>https://exemple.fr/sans-titre</link>
    </item>
  </channel>
</rss>
"""


def test_parse_edge_cases():
    articles = parse_feed(FEED_WITH_EDGE_CASES, LE_MONDE, FETCHED_AT)

    assert len(articles) == 1  # items sans titre ou sans lien ignorés
    article = articles[0]
    assert article["title"] == "Titre & gras"
    assert article["summary"] == "Un chapô avec espaces"
    assert article["url"] == "https://exemple.fr/a"
    assert article["published_at"] is None  # pas de date : le repli se fera au nettoyage
    assert "Dupont" not in str(article)  # jamais l'auteur (RGPD)


def test_parse_garbage_raises():
    with pytest.raises(ValueError, match="Flux illisible"):
        parse_feed(b"<html>Access Denied</html", LE_MONDE, FETCHED_AT)


def test_html_to_text():
    assert html_to_text("<p>a&nbsp;<i>b</i>\n\nc</p>") == "a b c"


def test_truncate_cuts_on_word_boundary():
    text = "mot " * 100
    result = truncate(text, 20)
    assert len(result) <= 20
    assert result.endswith("…")
    assert result == "mot mot mot mot…"
    assert truncate("court", 20) == "court"
