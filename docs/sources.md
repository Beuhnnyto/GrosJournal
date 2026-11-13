# Sources

Les URL de `sources.csv` ont été vérifiées le 13/11/2026 avec `curl` et recoupées avec
l'annuaire [Atlas des flux](https://atlasflux.saynete.com/). Pour chaque titre, l'atlas a une page
dédiée (par exemple `atlas_des_flux_rss_fra_dedie_le_monde.htm`), exportable en `.csv`, `.xml` et `.opml`.

| Source | Statut | Remarque |
|---|---|---|
| Ouest-France | ✅ 200 | `cache-control: no-cache`, ni ETag ni Last-Modified ; liens avec `utm_*` (à nettoyer au TD 3) |
| La Voix du Nord | ❌ 403 | Akamai bloque aussi `robots.txt` ; même blocage sur le flux « une » de l'atlas (`/destinations/2/cible_principale/rss`) → `actif=non` |
| Sud Ouest | ✅ 200 | `max-age=600` |
| Le Télégramme | ⚠️ | `/rss.xml` en 403 ; `/bretagne/rss.xml` (trouvé dans l'atlas) en 200 |
| La Dépêche du Midi | ✅ 200 | 100 items, dont certains datent de plus d'un an : le filtre < 24 h est indispensable |
| Le Monde | ✅ 200 | `must-revalidate`, ni ETag ni Last-Modified |
| Libération | ✅ 200 | **ETag + Last-Modified** |
| Le Figaro | ✅ 200 | `max-age=600` |
| Les Échos | ❌ 503/403 | absent de l'atlas → `actif=non` |
| La Croix | ✅ 200 | redirige vers `/feeds/rss/site.xml` ; **ETag + Last-Modified** |

Résultat : 8 sources actives (4 PQR, 4 PQN), comme l'exige le cadrage.

**Pour le TD 3** : les requêtes conditionnelles (`If-None-Match` / `If-Modified-Since`) ne
serviront que pour Libération et La Croix ; pour les autres flux, on dédoublonne par `id` (hash
de l'URL), ce que fait déjà `ON CONFLICT DO NOTHING`.
