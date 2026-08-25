"""
Configuration du logging (loguru), partagee par tous les blocs.

Evite de dupliquer le meme setup (logger.remove()/logger.add(...)) dans
chaque run.py / api.py : un bloc appelle simplement configurer_logger()
et recoit un logger deja branche sur la console et sur le fichier de log
du projet (commun/config.py::FICHIER_LOG).
"""

from loguru import logger

from commun.config import FICHIER_LOG, FORMAT_LOG


def configurer_logger():
    """Configure loguru (console + fichier) et retourne le logger a utiliser."""
    logger.remove()
    logger.add(lambda msg: print(msg, end=""), format=FORMAT_LOG)
    logger.add(FICHIER_LOG, format=FORMAT_LOG)
    return logger
