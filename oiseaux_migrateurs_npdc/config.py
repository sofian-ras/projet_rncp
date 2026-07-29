"""
Configuration - Réexporte depuis scripts.config
"""

try:
    from scripts.config import (
        ParametresAPI,
        ParametresAcquisition,
        ParametresNettoyage,
        ParametresFeatures,
        ParametresML,
        ParametresDL,
        FORMAT_LOG,
        ESPECES,
        ZONE_GEOGRAPHIQUE,
        REPERTOIRE_DONNEES,
        REPERTOIRE_DONNEES_BRUTES,
        REPERTOIRE_DONNEES_TRAITEES,
        REPERTOIRE_CARACTERISTIQUES,
        REPERTOIRE_MODELES,
        REPERTOIRE_RACINE,
        REPERTOIRE_SCRIPTS,
        FICHIER_LOG,
    )
except ModuleNotFoundError:
    from .scripts.config import (
        ParametresAPI,
        ParametresAcquisition,
        ParametresNettoyage,
        ParametresFeatures,
        ParametresML,
        ParametresDL,
        FORMAT_LOG,
        ESPECES,
        ZONE_GEOGRAPHIQUE,
        REPERTOIRE_DONNEES,
        REPERTOIRE_DONNEES_BRUTES,
        REPERTOIRE_DONNEES_TRAITEES,
        REPERTOIRE_CARACTERISTIQUES,
        REPERTOIRE_MODELES,
        REPERTOIRE_RACINE,
        REPERTOIRE_SCRIPTS,
        FICHIER_LOG,
    )

__all__ = [
    "ParametresAPI",
    "ParametresAcquisition",
    "ParametresNettoyage",
    "ParametresFeatures",
    "ParametresML",
    "ParametresDL",
    "FORMAT_LOG",
    "ESPECES",
    "ZONE_GEOGRAPHIQUE",
    "REPERTOIRE_DONNEES",
    "REPERTOIRE_DONNEES_BRUTES",
    "REPERTOIRE_DONNEES_TRAITEES",
    "REPERTOIRE_CARACTERISTIQUES",
    "REPERTOIRE_MODELES",
    "REPERTOIRE_RACINE",
    "REPERTOIRE_SCRIPTS",
    "FICHIER_LOG",
]
