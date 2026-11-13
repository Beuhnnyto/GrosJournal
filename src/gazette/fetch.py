"""Téléchargement d'un flux."""

import httpx


def fetch(url: str, user_agent: str, timeout: float) -> bytes:
    response = httpx.get(
        url, headers={"User-Agent": user_agent}, timeout=timeout, follow_redirects=True
    )
    response.raise_for_status()
    return response.content
