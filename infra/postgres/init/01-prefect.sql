-- Exécuté une seule fois, à la création du volume : base dédiée au serveur Prefect.
-- La base `gazette` (POSTGRES_DB) est créée par l'image ; son schéma est géré par l'app.
CREATE DATABASE prefect;
