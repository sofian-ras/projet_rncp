# BC01 — Schéma d'infrastructure de données (1 page)

## Vue d'ensemble

```
   SOURCES EXTERNES              INGESTION (acquisition.py)     DATA LAKE
 +------------------+          +-----------------------+       MinIO bucket donnees-brutes
 |  API GBIF        | -------> |  telecharger GBIF     | ----> observations_gbif.csv
 |  (observations)  |  HTTP    |  pagination + retry   |       (repli : donnees/brutes/)
 +------------------+          +-----------------------+
 +------------------+          +-----------------------+
 |  API Open-Meteo  | -------> |  telecharger meteo    | ----> meteo_npdc.csv
 |  (météo 6 ans)   |  HTTP    |  1 requête + retry    |
 +------------------+          +-----------------------+
                                                                            |
                                                                            v
                              ETL (nettoyage.py)              DATA WAREHOUSE
 +----------------------------------------------+       MongoDB (repli : donnees/traitees/*.parquet)
 | 1. suppression des lignes incomplètes        |       + MinIO bucket donnees-traitees
 | 2. validation des coordonnées GPS            | ----> observations_nettoyees
 | 3. filtrage géographique (zone NPDC)          |       grille_presence_hebdo
 | 4. uniformisation des dates                   |       meteo_processed
 | 5. déduplication                              |       etl_journal (trace des passages)
 | 6. agrégation -> grille hebdo présence/absence|
 +----------------------------------------------+
                                                                            |
                                                                            v
                                                          CONSOMMATEURS
                                          BC02 (analyse) · BC03 (ML) · BC05 (API + dashboard)
```

> `STORAGE_BACKEND=local` (défaut) : seuls les fichiers de `donnees/` sont écrits/lus.
> `STORAGE_BACKEND=objet` (docker-compose) : MinIO + MongoDB deviennent la source de vérité,
> les fichiers locaux servent de repli.

## Choix techniques et justification

| Besoin | Choix | Pourquoi |
|---|---|---|
| Stockage brut (data lake) | **MinIO** (objet, S3-compatible), bucket `donnees-brutes` — repli fichiers `donnees/brutes/*.csv` | Données semi-structurées telles que renvoyées par les API, aucune perte ; stockage objet = cible standard d'un data lake (C1.1) |
| Stockage exploitable (warehouse) | **MongoDB**, collections `observations_nettoyees` / `grille_presence_hebdo` / `meteo_processed` — repli **Parquet** `donnees/traitees/` | Base requêtable par les autres équipes (C1.4) ; le Parquet colonnaire reste la fixture d'entrée versionnée pour un clone sans Docker |
| Orchestration | `run.py` (acquisition → nettoyage → chargement MinIO/MongoDB) | Volume actuel ~5 Mo : un script séquentiel suffit, pas besoin d'Airflow |
| Environnement | **docker-compose** (`docker-compose.yml` à la racine) : MinIO + MongoDB + MLflow + API + dashboard | Un seul `docker compose up` lève toute l'infra, reproductible sur toute machine (rejoint C5.1) |
| Robustesse de la collecte | `get_avec_retry` (backoff exponentiel sur 5xx / timeout) | GBIF renvoie des 503 transitoires ; sans réessai la collecte repartait vide |
| Calcul distribué | **Non utilisé** | ~680 k lignes traitées en < 2 s par pandas ; Spark n'apporterait rien à ce volume |

### Bascule local / objet

Le pipeline écrit et lit au choix sur disque ou dans MinIO/MongoDB, via la variable
`STORAGE_BACKEND` (`commun/config.py::ParametresStockage`) :

- `local` (défaut) : uniquement les fichiers de `donnees/` — le projet tourne après un simple `git clone`.
- `objet` : BC01 dépose en plus les CSV/Parquet dans MinIO et les tables dans MongoDB ;
  `commun/chargement.py` sert alors BC02–BC05 depuis MongoDB (avec repli automatique sur le
  Parquet local si l'infra est absente). Les clients (`commun/stockage.py`, classes `ClientMinio` /
  `ClientMongo`) reprennent le patron du cours *AWS S3 et MinIO* (paquets `minio` + `pymongo`).

## Coûts

Infrastructure actuelle : **0 € / mois**. Sources 100 % publiques et gratuites (GBIF, Open-Meteo, sans clé d'API), stockage sur disque local, aucun service cloud.

## Infrastructure `objet` (docker-compose)

```
  Sources ---> acquisition.py ---> MinIO  bucket donnees-brutes    (CSV : data lake)
   GBIF                      \
   Open-Meteo                 `-> nettoyage.py (ETL)
                                     |
                                     +-> MinIO  bucket donnees-traitees  (Parquet)
                                     +-> MongoDB  observations_nettoyees
                                     +-> MongoDB  grille_presence_hebdo   <-- BC03 / BC05 lisent ici
                                     +-> MongoDB  meteo_processed
                                     +-> MongoDB  etl_journal  (trace de chaque passage)

  BC03 --> MLflow (conteneur, artefacts sur MinIO bucket mlflow) + push pipeline_ml.pkl -> MinIO bucket modeles
  BC05 --> API récupère pipeline_ml.pkl depuis MinIO ; dashboard lit MongoDB via commun/chargement.py
```

Lancement : `docker compose up -d --build` (infra + API + dashboard), puis
`docker compose --profile pipeline run --rm bc01` pour peupler MinIO/MongoDB.
Consoles : MinIO `:9001`, Mongo Express `:8081`, MLflow `:5000`, API `:8000/docs`, dashboard `:8501`.

### Au-delà (si le volume le justifiait)

Spark pour l'ETL distribué et un entrepôt colonne (Redshift / BigQuery) deviennent pertinents
au-delà de ~10 Go de données brutes ou d'un besoin de fraîcheur temps réel. En l'état
(~5 Mo, ~680 k lignes), MinIO + MongoDB couvrent le besoin sans calcul distribué.

## Conformité RGPD

Le processus de collecte est **hors périmètre RGPD** : aucune donnée à caractère personnel n'est
collectée ni stockée.

- **Observations GBIF** : données d'occurrence d'espèces (position, date, taxon). Les identifiants
  d'observateurs ne sont pas demandés (`fields=` limite la réponse à `gbifID, scientificName,
  eventDate, decimalLatitude, decimalLongitude, coordinateUncertaintyInMeters, country`).
- **Météo Open-Meteo** : mesures physiques agrégées par point géographique, sans lien à une personne.
- **Licences** : GBIF expose les occurrences sous licences ouvertes (CC0 / CC-BY / CC-BY-NC selon le
  jeu) ; Open-Meteo est réutilisable librement (attribution). Les URL sources sont tracées dans le
  code (`acquisition.py`).
- **Minimisation** : seules les colonnes utiles au modèle sont conservées après l'ETL.

Si le projet devait un jour ingérer des données de science citoyenne nominatives (pseudo
d'observateur, par ex.), il faudrait : pseudonymisation à l'ingestion, registre de traitement,
base légale (intérêt légitime), et information des personnes concernées.
