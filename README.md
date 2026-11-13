# La gazette

Chaque matin, une « édition » qui répond à une question : **de quoi parlent les rédactions
françaises aujourd'hui ?** Voir la [note de cadrage](docs/cadrage.md).

État actuel (TD 2) : collecte des flux RSS de `sources.csv`, orchestrée par **Prefect**,
stockée en brut (fichiers) et dans **PostgreSQL**.

## Lancer (seul Docker est requis)

```bash
git clone https://github.com/Beuhnnyto/GrosJournal.git && cd GrosJournal
bin/dev
```

`bin/dev` démarre trois conteneurs (`docker-compose.yml`) :

| Service    | Rôle                                                                      |
|------------|---------------------------------------------------------------------------|
| `postgres` | bases `gazette` (articles) et `prefect` (historique des runs)             |
| `prefect`  | serveur Prefect, UI sur <http://localhost:4200>                           |
| `worker`   | sert le flow `ingest-feeds`, planifié tous les jours à 5 h 30 (Paris)     |

Lancer une collecte tout de suite :

```bash
docker compose exec worker gazette ingest
# ou : docker compose exec worker prefect deployment run 'ingest-feeds/quotidien'
```

Résultats :

- `data/raw/AAAA-MM-JJ/<source>-HHMMSS.xml` : le flux tel que reçu ;
- `data/raw/AAAA-MM-JJ/<source>-HHMMSS.json` : les articles parsés ;
- table `articles` dans Postgres (un article = une URL, les doublons sont ignorés) :
  `docker compose exec postgres psql -U gazette -c 'select source, count(*) from articles group by 1'`.

Arrêter : `docker compose down` (ajouter `-v` pour effacer aussi la base).

### Ce PC comme serveur

La stack tourne en continu (`restart: unless-stopped`) : le flow se déclenche à 5 h 30 tant que
Docker tourne. Par défaut, l'UI et Postgres ne sont joignables que depuis ce PC. Pour ouvrir
l'UI au réseau local : `cp .env.example .env`, mettre `BIND_ADDR=0.0.0.0`, puis relancer `bin/dev`.
Le serveur Prefect n'a pas d'authentification : on ne l'expose pas sur Internet.

## Tester

```bash
bin/test
```

Lance dans un conteneur les mêmes vérifications que la CI : `ruff check`, `ruff format --check`
et `pytest`. Si `uv` est installé : `uv sync` puis `uv run pytest`.

## Arborescence

```
src/gazette/   sources.py (lecture de sources.csv) · fetch.py · parse.py · storage.py
               flows.py (flow Prefect) · cli.py (commande `gazette`)
tests/         tests unitaires ; tests/fixtures/ = flux réels enregistrés
infra/         init Postgres
docs/          cadrage, CI/CD, sources
bin/           dev, test
```

Ajouter ou couper une source : éditer `sources.csv` (colonne `actif` = `oui`/`non`, l'URL est la
première URL de la colonne `acces`). Le fichier est monté dans le worker : pas besoin de
reconstruire l'image. Voir [docs/sources.md](docs/sources.md).

## Contribuer

Voir [CONTRIBUTING.md](CONTRIBUTING.md) et la stratégie CI/CD dans [docs/ci-cd.md](docs/ci-cd.md).
