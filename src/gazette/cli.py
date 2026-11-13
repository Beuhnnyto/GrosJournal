"""Point d'entrée `gazette`."""

import argparse

from gazette.flows import ingest_feeds


def main() -> None:
    parser = argparse.ArgumentParser(prog="gazette")
    sub = parser.add_subparsers(dest="command", required=True)
    ingest = sub.add_parser("ingest", help="collecter toutes les sources maintenant")
    ingest.add_argument("--sources", help="chemin vers sources.csv")
    sub.add_parser("serve", help="servir le flow avec son planning quotidien (5 h 30)")
    args = parser.parse_args()

    if args.command == "ingest":
        ingest_feeds(sources_path=args.sources)
    elif args.command == "serve":
        from prefect.schedules import Cron

        ingest_feeds.serve(
            name="quotidien", schedules=[Cron("30 5 * * *", timezone="Europe/Paris")]
        )


if __name__ == "__main__":
    main()
