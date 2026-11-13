# Contribuer

## Branches

- `main` est toujours déployable : on ne pousse jamais directement dessus.
- Une branche par sujet, nommée `<type>/<sujet-court>` : `feat/collecte-etag`,
  `fix/date-ouest-france`, `docs/readme`, `chore/ci-cache`.
- On ouvre une Pull Request vers `main`. Pour merger, il faut **une CI verte et une relecture**
  par un·e autre membre de l'équipe, même rapide.
- C'est l'auteur·e de la PR qui merge une fois la PR approuvée, en *squash merge*. On supprime
  la branche après le merge.

## Commits

Format [Conventional Commits](https://www.conventionalcommits.org/fr/) :
`<type>(<portée>): <résumé à l'impératif>`.

- Types : `feat`, `fix`, `docs`, `test`, `refactor`, `chore`, `ci`.
- Exemples : `feat(collecte): ajoute Sud Ouest`, `fix(parse): date absente -> None`.
- Un commit = une modification cohérente. Le message dit *pourquoi* quand ce n'est pas évident.

## Avant de pousser

```bash
bin/test          # lint + format + tests, comme la CI
```

Un nouveau parseur ou une nouvelle source arrive avec un test et, si possible, une fixture
enregistrée dans `tests/fixtures/` (le flux réel, récupéré avec `curl`).

## Règles du projet

- Rien de ce qui tourne n'est installé à la main : tout est décrit dans le dépôt
  (`Dockerfile`, `docker-compose.yml`, `infra/`).
- On ne garde jamais le nom des auteurs ni le corps des articles (voir la note de cadrage).
- On ne contourne pas un blocage d'éditeur (403, anti-bot) : la source passe à `actif=non`.
- Pas de secret dans le dépôt : `.env` est ignoré par git, `.env.example` sert de modèle.
