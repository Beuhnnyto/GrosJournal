"""Flow Prefect : collecte de toutes les sources actives."""

from datetime import UTC, datetime
from pathlib import Path

import psycopg
from prefect import flow, get_run_logger, task

from gazette.config import Settings
from gazette.fetch import fetch
from gazette.parse import parse_feed
from gazette.sources import load_sources
from gazette.storage import ensure_schema, insert_articles, write_raw


@task(name="fetch-feed", task_run_name="fetch-{slug}", retries=3, retry_delay_seconds=[10, 30, 60])
def fetch_feed(slug: str, url: str, user_agent: str, timeout: float) -> bytes:
    return fetch(url, user_agent, timeout)


@flow(name="ingest-feeds")
def ingest_feeds(sources_path: str | None = None) -> dict[str, int]:
    """Lit chaque flux, l'archive en brut puis insère les articles dans PostgreSQL.

    Une source en échec n'empêche pas les autres d'être traitées ; le run finit
    en échec à la fin s'il y en a eu au moins une.
    """
    logger = get_run_logger()
    settings = Settings.from_env()
    sources = load_sources(Path(sources_path) if sources_path else settings.sources_path)
    fetched_at = datetime.now(UTC)

    futures = [
        (s, fetch_feed.submit(s.slug, s.url, settings.user_agent, settings.http_timeout))
        for s in sources
    ]

    inserted: dict[str, int] = {}
    failures: list[str] = []
    with psycopg.connect(settings.database_url) as conn:
        ensure_schema(conn)
        for source, future in futures:
            try:
                content = future.result()
                articles = parse_feed(content, source, fetched_at)
                path = write_raw(settings.data_dir, source, fetched_at, content, articles)
                inserted[source.name] = insert_articles(conn, articles)
            except Exception as exc:
                logger.error("%s : échec (%s)", source.name, exc)
                failures.append(source.name)
                continue
            if not articles:
                logger.warning("%s : 0 article dans le flux", source.name)
            logger.info(
                "%s : %d articles lus, %d nouveaux -> %s",
                source.name,
                len(articles),
                inserted[source.name],
                path,
            )

    if failures:
        raise RuntimeError(f"Sources en échec : {', '.join(failures)}")
    return inserted
