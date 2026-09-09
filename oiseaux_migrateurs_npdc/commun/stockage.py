"""
Stockage objet du projet : data lake MinIO (fichiers) + entrepot MongoDB
(donnees requetables). Mis en place par BC01, consomme par BC02..BC05.

Reprend le patron du cours "AWS S3 et MinIO" (une classe cliente par service,
paquets `minio` et `pymongo`) adapte au projet :
  - ClientMinio : depose / recupere des fichiers (CSV, Parquet, .pkl, images)
    dans des buckets S3 -> role de data lake (C1.1).
  - ClientMongo : ecrit / lit des DataFrames dans des collections MongoDB
    -> entrepot requetable, "donnees disponibles et comprehensibles" (C1.4).

N'est utilise que si STORAGE_BACKEND=objet (docker-compose.yml). En mode
"local", les blocs gardent leur repli sur les fichiers de donnees/.
Les imports de `minio` / `pymongo` sont differes : ces paquets ne sont
requis que lorsque le backend objet est actif.
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import pandas as pd
from loguru import logger

from commun.config import ParametresStockage


# ---------------------------------------------------------------------------
# MinIO : data lake (fichiers)
# ---------------------------------------------------------------------------

class ClientMinio:
    """Client MinIO : un bucket par nature de donnee, cree au besoin."""

    BUCKETS = (
        ParametresStockage.BUCKET_BRUTES,
        ParametresStockage.BUCKET_TRAITEES,
        ParametresStockage.BUCKET_MODELES,
        ParametresStockage.BUCKET_SORTIES,
        ParametresStockage.BUCKET_MLFLOW,
    )

    def __init__(self) -> None:
        from minio import Minio  # dependance optionnelle : import differe

        self.client = Minio(
            endpoint=ParametresStockage.MINIO_ENDPOINT,
            access_key=ParametresStockage.MINIO_ACCESS_KEY,
            secret_key=ParametresStockage.MINIO_SECRET_KEY,
            secure=ParametresStockage.MINIO_SECURE,
        )
        self._assurer_buckets()

    def _assurer_buckets(self) -> None:
        for bucket in self.BUCKETS:
            if not self.client.bucket_exists(bucket):
                self.client.make_bucket(bucket)
                logger.info(f"MinIO : bucket cree '{bucket}'")

    def televerser_fichier(self, chemin_local, bucket: str, nom_objet: str | None = None) -> str:
        """Depose un fichier du disque dans un bucket. Retourne l'URI s3://."""
        chemin_local = Path(chemin_local)
        nom_objet = nom_objet or chemin_local.name
        self.client.fput_object(bucket, nom_objet, str(chemin_local))
        uri = f"s3://{bucket}/{nom_objet}"
        logger.info(f"MinIO : {uri} ({chemin_local.stat().st_size // 1024} Ko)")
        return uri

    def televerser_dossier(self, dossier, bucket: str, motif: str = "*") -> list[str]:
        """Depose tous les fichiers d'un dossier (non recursif) correspondant au motif."""
        dossier = Path(dossier)
        uris = []
        for fichier in sorted(dossier.glob(motif)):
            if fichier.is_file():
                uris.append(self.televerser_fichier(fichier, bucket))
        return uris

    def telecharger_fichier(self, bucket: str, nom_objet: str, chemin_local) -> Path:
        """Recupere un objet vers un fichier local (cree les dossiers parents)."""
        chemin_local = Path(chemin_local)
        chemin_local.parent.mkdir(parents=True, exist_ok=True)
        self.client.fget_object(bucket, nom_objet, str(chemin_local))
        logger.info(f"MinIO : {bucket}/{nom_objet} -> {chemin_local}")
        return chemin_local

    def lister(self, bucket: str, prefixe: str = "") -> list[dict]:
        objets = self.client.list_objects(bucket, prefix=prefixe, recursive=True)
        return [{"nom": o.object_name, "taille": o.size, "modifie": o.last_modified} for o in objets]

    def url_presignee(self, bucket: str, nom_objet: str, heures: int = 24) -> str:
        """URL temporaire de telechargement direct (utile pour une demo)."""
        from datetime import timedelta

        return self.client.presigned_get_object(bucket, nom_objet, expires=timedelta(hours=heures))


# ---------------------------------------------------------------------------
# MongoDB : entrepot requetable (DataFrames <-> collections)
# ---------------------------------------------------------------------------

class ClientMongo:
    """Client MongoDB : une collection par table produite par l'ETL de BC01."""

    def __init__(self) -> None:
        from pymongo import MongoClient  # dependance optionnelle : import differe

        self.client = MongoClient(ParametresStockage.uri_mongo(), serverSelectionTimeoutMS=5000)
        self.db = self.client[ParametresStockage.MONGO_DB]

    # --- ecriture ---

    def ecrire_dataframe(self, nom_collection: str, df: pd.DataFrame, taille_lot: int = 10_000) -> int:
        """Remplace le contenu d'une collection par les lignes du DataFrame.

        L'ETL de BC01 recalcule tout a chaque passage : on vide puis on reinsere
        (plutot qu'un upsert ligne a ligne, la grille faisant des centaines de
        milliers de lignes). Le passage par JSON neutralise les types numpy et
        les NaN, que pymongo ne sait pas encoder directement.
        """
        collection = self.db[nom_collection]
        collection.delete_many({})
        if df is None or df.empty:
            logger.warning(f"Mongo : '{nom_collection}' laisse vide (DataFrame vide)")
            return 0

        enregistrements = json.loads(df.to_json(orient="records", date_format="iso"))
        total = 0
        for debut in range(0, len(enregistrements), taille_lot):
            lot = enregistrements[debut : debut + taille_lot]
            collection.insert_many(lot, ordered=False)
            total += len(lot)
        logger.info(f"Mongo : '{nom_collection}' <- {total} documents")
        return total

    def journaliser_etl(self, statut: str, details: dict) -> None:
        """Trace un passage de l'ETL BC01 dans la collection 'etl_journal'."""
        self.db["etl_journal"].insert_one(
            {"horodatage": datetime.now(timezone.utc), "statut": statut, **details}
        )

    # --- lecture ---

    def lire_dataframe(self, nom_collection: str, colonnes_dates: Iterable[str] = ()) -> pd.DataFrame:
        """Charge une collection entiere en DataFrame (sans le champ _id)."""
        documents = list(self.db[nom_collection].find({}, {"_id": 0}))
        cadre = pd.DataFrame(documents)
        for colonne in colonnes_dates:
            if colonne in cadre.columns:
                cadre[colonne] = pd.to_datetime(cadre[colonne])
        return cadre

    def compter(self, nom_collection: str) -> int:
        return self.db[nom_collection].count_documents({})

    def fermer(self) -> None:
        self.client.close()
