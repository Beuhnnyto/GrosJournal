import json
from datetime import UTC, datetime

from gazette.sources import Source
from gazette.storage import write_raw


def test_write_raw(tmp_path):
    source = Source("Le Monde", "PQN", "National", "u")
    fetched_at = datetime(2026, 11, 13, 5, 30, 12, tzinfo=UTC)
    articles = [{"id": "1", "title": "Été"}]

    path = write_raw(tmp_path, source, fetched_at, b"<rss/>", articles)

    assert path == tmp_path / "raw" / "2026-11-13" / "le-monde-053012.json"
    assert json.loads(path.read_text(encoding="utf-8")) == articles
    assert path.with_suffix(".xml").read_bytes() == b"<rss/>"
