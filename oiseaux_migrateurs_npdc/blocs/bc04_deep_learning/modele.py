"""
BC04 - Architecture du reseau de neurones (Embedding + LSTM + Dense) et
utilitaire de decodage des critiques IMDB.

Separe de run.py (qui orchestre chargement des donnees, entrainement,
evaluation et sauvegarde) pour ne pas melanger la definition du modele
avec l'orchestration.
"""

import numpy as np

from commun.config import ParametresDL


def construire_modele(taille_vocabulaire: int, longueur_sequence: int):
    """Construit l'architecture Embedding + LSTM + Dense"""
    from tensorflow import keras
    from tensorflow.keras import layers

    modele = keras.Sequential([
        layers.Input(shape=(longueur_sequence,)),
        layers.Embedding(input_dim=taille_vocabulaire, output_dim=ParametresDL.TAILLE_EMBEDDING),
        layers.LSTM(ParametresDL.UNITES_LSTM, dropout=ParametresDL.DROPOUT_RATE),
        layers.Dense(1, activation="sigmoid"),
    ])
    modele.compile(optimizer="adam", loss="binary_crossentropy", metrics=["accuracy"])
    return modele


def decoder_avis(sequence: np.ndarray, index_mots: dict) -> str:
    """Retraduit une sequence de numeros de mots en texte lisible (pour la demo)"""
    index_inverse = {valeur: cle for cle, valeur in index_mots.items()}
    # Keras decale les indices de 3 (0=padding, 1=debut, 2=mot inconnu)
    mots = [index_inverse.get(i - 3, "?") for i in sequence if i > 2]
    return " ".join(mots)
