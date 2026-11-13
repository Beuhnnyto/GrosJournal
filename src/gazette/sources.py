"""Lecture de sources.csv."""

import csv
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path

URL_RE = re.compile(r"https?://\S+")


@dataclass(frozen=True)
class Source:
    name: str
    type: str
    region: str
    url: str

    @property
    def slug(self) -> str:
        ascii_name = unicodedata.normalize("NFKD", self.name).encode("ascii", "ignore").decode()
        return re.sub(r"[^a-z0-9]+", "-", ascii_name.lower()).strip("-")


def load_sources(path: Path, only_active: bool = True) -> list[Source]:
    """Charge les sources ; l'URL du flux est la première URL de la colonne `acces`."""
    sources = []
    # utf-8-sig : accepte le BOM ajouté par Excel / LibreOffice
    with path.open(encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            if only_active and row.get("actif", "oui").strip().lower() != "oui":
                continue
            match = URL_RE.search(row["acces"])
            if match is None:
                raise ValueError(f"Pas d'URL dans la colonne acces pour {row['nom']!r}")
            sources.append(
                Source(name=row["nom"], type=row["type"], region=row["region"], url=match.group())
            )
    return sources
