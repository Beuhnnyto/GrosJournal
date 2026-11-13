# Stratégie CI/CD

1. **Déclencheurs** : la CI (`.github/workflows/ci.yml`) tourne sur chaque Pull Request et à chaque push sur `main`.
2. **Lint** : `ruff check` et `ruff format --check`.
3. **Tests** : `pytest`, sur des fixtures enregistrées, sans réseau ni base.
4. **Build** : image Docker multi-étapes (cible `runtime`), avec un utilisateur non root ; seul le venv est copié dans l'image finale.
5. **Push** : seulement sur `main`, vers `ghcr.io/beuhnnyto/grosjournal`, avec le tag `YYYYMMDDHHMMSS-sha` (UTC + 7 caractères du commit) et `latest`. Sur une PR, l'image est construite mais pas publiée.
6. Le build n'est lancé que si le lint et les tests sont verts : une CI rouge ne publie rien.
7. **Merge** : une protection de branche sur `main` exige que les checks `lint`, `test` et `image` soient verts, ainsi qu'une relecture.
8. **Reproductibilité** : les versions sont figées par `uv.lock` ; `bin/test` rejoue en local les vérifications de la CI.
9. **Hors périmètre aujourd'hui** : pas de déploiement automatique (prévu au TD 7), pas de matrice de versions.
10. **Retrouver une image** : le tag donne le commit exact (`git show <sha>`), et le label OCI `revision` le contient aussi.
