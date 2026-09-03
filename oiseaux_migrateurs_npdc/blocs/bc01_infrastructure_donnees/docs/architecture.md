# BC01 — Schéma d'infrastructure de données (1 page)

## Vue d'ensemble

```
   SOURCES EXTERNES              INGESTION (acquisition.py)         DATA LAKE (donnees/brutes/)
 +------------------+          +-----------------------+          +------------------------+
 |  API GBIF        | -------> |  AcquisiteurGBIF      | -------> |  observations_gbif.csv |
 |  (observations)  |  HTTP    |  pagination + retry   |  écrit   |                        |
 +------------------+          +-----------------------+          +------------------------+
 +------------------+          +-----------------------+          +------------------------+
 |  API Open-Meteo  | -------> |  AcquisiteurMeteo     | -------> |  meteo_npdc.csv        |
 |  (météo 6 ans)   |  HTTP    |  1 requête + retry    |  écrit   |                        |
 +------------------+          +-----------------------+          +------------------------+
                                                                            |
                                                                            v
                              ETL (nettoyage.py)                  DATA WAREHOUSE (donnees/traitees/)
 +----------------------------------------------+          +-----------------------------------+
 | 1. suppression des lignes incomplètes        |          | observations_nettoyees.parquet    |
 | 2. validation des coordonnées GPS            | -------> | grille_presence_hebdo.parquet     |
 | 3. filtrage géographique (zone NPDC)          |  écrit   | meteo_processed.parquet           |
 | 4. uniformisation des dates                   |          |                                   |
 | 5. déduplication                              |          | format colonnaire, typé, requêtable|
 | 6. agrégation -> grille hebdo présence/absence|          |                                   |
 +----------------------------------------------+          +-----------------------------------+
                                                                            |
                                                                            v
                                                          CONSOMMATEURS
                                          BC02 (analyse) · BC03 (ML) · BC05 (API + dashboard)
```

## Choix techniques et justification

| Besoin | Choix actuel | Pourquoi |
|---|---|---|
| Stockage brut (data lake) | Fichiers CSV dans `donnees/brutes/` | Données semi-structurées telles que renvoyées par les API, aucune perte |
| Stockage exploitable (warehouse) | Fichiers **Parquet** dans `donnees/traitees/` | Colonnaire, typé, compressé, lecture directe par pandas ; requêtable sans serveur |
| Orchestration | `run.py` (acquisition → nettoyage) | Volume actuel ~5 Mo : un script séquentiel suffit, pas besoin d'Airflow |
| Robustesse de la collecte | `get_avec_retry` (backoff exponentiel sur 5xx / timeout) | GBIF renvoie des 503 transitoires ; sans réessai la collecte repartait vide |
| Calcul distribué | **Non utilisé** | ~680 k lignes traitées en < 2 s par pandas ; Spark n'apporterait rien à ce volume |

## Coûts

Infrastructure actuelle : **0 € / mois**. Sources 100 % publiques et gratuites (GBIF, Open-Meteo, sans clé d'API), stockage sur disque local, aucun service cloud.

## Cible d'industrialisation (si le volume le justifiait)

```
  Sources ---> Ingestion ---> MinIO (data lake S3)  ---> Spark (ETL distribué)
                                                            |
                                                            v
                                          PostgreSQL (data warehouse + métadonnées)
                                                            |
                                                            v
                                          BC03 / BC05 (via connecteurs SQL)
```

Bascule envisagée au-delà de ~10 Go de données brutes ou d'un besoin de fraîcheur temps réel.
Ordre de grandeur : MinIO + PostgreSQL managés ≈ 20–40 € / mois ; cluster Spark à la demande
uniquement pendant les recalculs.

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
