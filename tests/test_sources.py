from pathlib import Path

import pytest

from gazette.sources import Source, load_sources

REPO_SOURCES = Path(__file__).parent.parent / "sources.csv"


def test_load_repo_sources_skips_inactive():
    sources = load_sources(REPO_SOURCES)
    names = {s.name for s in sources}

    assert "Le Monde" in names
    assert "La Voix du Nord" not in names
    assert all(s.url.startswith("https://") for s in sources)
    assert sum(s.type == "PQR" for s in sources) >= 4
    assert sum(s.type == "PQN" for s in sources) >= 4


def test_url_is_extracted_from_acces_column():
    by_name = {s.name: s for s in load_sources(REPO_SOURCES, only_active=False)}

    assert by_name["Ouest-France"].url == "https://www.ouest-france.fr/rss/une"
    assert by_name["Libération"].url.endswith("accueil-une/?outputType=xml")


def test_missing_url_raises(tmp_path):
    csv_path = tmp_path / "sources.csv"
    csv_path.write_text("nom,type,region,acces,actif\nX,PQN,National,pas d'url,oui\n")
    with pytest.raises(ValueError, match="Pas d'URL"):
        load_sources(csv_path)


def test_slug():
    assert Source("La Dépêche du Midi", "PQR", "Occitanie", "u").slug == "la-depeche-du-midi"
    assert Source("Les Échos", "PQN", "National", "u").slug == "les-echos"
