"""
BC04 - Deep Learning : prediction sur donnees NON structurees (texte)
========================================================================

Ce script est AUTONOME : contrairement a BC01-BC03 (qui travaillent sur les
donnees tabulaires du projet ornithologique), il demontre la competence RNCP
"prediction par IA sur donnees non structurees" avec un cas d'usage classique
et reproductible : l'analyse de sentiment de critiques de films (jeu de
donnees IMDB, integre a TensorFlow/Keras).

Pourquoi un jeu de donnees different du reste du projet ?
------------------------------------------------------------
Le referentiel RNCP distingue explicitement deux competences :
  - BC03 : prediction sur donnees STRUCTUREES (un tableau de colonnes
    numeriques) -> deja demontre sur les donnees d'observations d'oiseaux
    (voir blocs/bc03_machine_learning).
  - BC04 : prediction sur donnees NON STRUCTUREES (texte, image, son) -> le
    jeu de donnees ornithologique de ce projet est un tableau, il ne
    convient donc pas pour demontrer CETTE competence precise. Le jeu IMDB
    (25 000 critiques de films en anglais, etiquetees positif/negatif) est
    un choix standard, gratuit, et integre a TensorFlow (pas de
    telechargement manuel a organiser), qui permet de montrer une vraie
    architecture de reseau de neurones sur du texte brut.

Architecture du modele (voir modele.py::construire_modele) :
  1. Embedding : transforme chaque mot (represente par un simple numero)
     en un vecteur de nombres qui capture un peu de son "sens"
     statistique -- deux mots au sens proche auront des vecteurs proches.
  2. LSTM (Long Short-Term Memory) : lit la critique mot par mot, en
     gardant en memoire le contexte des mots precedents. Utile pour du
     texte, ou l'ordre des mots change le sens ("pas bien" != "bien").
  3. Dense (1 neurone, activation sigmoide) : sortie finale, une
     probabilite entre 0 (critique negative) et 1 (critique positive).

Utilisation :
    python blocs/bc04_deep_learning/run.py

Remarque : le premier lancement telecharge le jeu de donnees IMDB (~17 Mo,
une seule fois, mis en cache localement par Keras dans ~/.keras/) -- une
connexion internet est donc necessaire au moins une fois avant la
demonstration devant le jury. Les lancements suivants sont hors-ligne.
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from commun.config import REPERTOIRE_MODELES, REPERTOIRE_RACINE, ParametresDL
from commun.journalisation import configurer_logger
from modele import construire_modele, decoder_avis

RACINE_PROJET = REPERTOIRE_RACINE
logger = configurer_logger()


def main() -> None:
    print("\n" + "#" * 70)
    print("# BC04 - DEEP LEARNING (donnees non structurees : texte)")
    print("#" * 70 + "\n")

    logger.info("Chargement de TensorFlow/Keras (peut prendre quelques secondes)...")
    from tensorflow import keras
    from tensorflow.keras.datasets import imdb
    from tensorflow.keras.preprocessing.sequence import pad_sequences
    from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, roc_auc_score

    keras.utils.set_random_seed(ParametresDL.RANDOM_STATE)

    logger.info("Chargement du jeu de donnees IMDB (25 000 critiques de films)...")
    (X_train_brut, y_train), (X_test_brut, y_test) = imdb.load_data(num_words=ParametresDL.NB_MOTS_VOCABULAIRE)

    # Sous-echantillonnage pour un entrainement rapide en demonstration
    rng = np.random.default_rng(ParametresDL.RANDOM_STATE)
    idx_train = rng.choice(len(X_train_brut), size=min(ParametresDL.TAILLE_ECHANTILLON_DEMO, len(X_train_brut)), replace=False)
    idx_test = rng.choice(len(X_test_brut), size=min(ParametresDL.TAILLE_ECHANTILLON_DEMO // 3, len(X_test_brut)), replace=False)
    X_train_brut, y_train = X_train_brut[idx_train], y_train[idx_train]
    X_test_brut, y_test = X_test_brut[idx_test], y_test[idx_test]

    logger.info(f"  Jeu d'entrainement : {len(X_train_brut)} critiques (sous-echantillon, pour une demo rapide)")
    logger.info(f"  Jeu de test         : {len(X_test_brut)} critiques")
    logger.info(f"  Vocabulaire retenu  : {ParametresDL.NB_MOTS_VOCABULAIRE} mots les plus frequents")

    X_train = pad_sequences(X_train_brut, maxlen=ParametresDL.LONGUEUR_SEQUENCE)
    X_test = pad_sequences(X_test_brut, maxlen=ParametresDL.LONGUEUR_SEQUENCE)

    logger.info("Construction du modele (Embedding + LSTM + Dense)...")
    modele = construire_modele(ParametresDL.NB_MOTS_VOCABULAIRE, ParametresDL.LONGUEUR_SEQUENCE)
    modele.summary()

    logger.info(f"Entrainement ({ParametresDL.EPOCHS} epochs)...")
    historique = modele.fit(
        X_train, y_train,
        validation_data=(X_test, y_test),
        epochs=ParametresDL.EPOCHS,
        batch_size=ParametresDL.BATCH_SIZE,
        verbose=2,
    )

    logger.info("Evaluation sur le jeu de test...")
    y_proba = modele.predict(X_test, verbose=0).ravel()
    y_pred = (y_proba > 0.5).astype(int)

    metriques = {
        "accuracy": float(accuracy_score(y_test, y_pred)),
        "f1_score": float(f1_score(y_test, y_pred)),
        "auc_roc": float(roc_auc_score(y_test, y_proba)),
    }
    logger.info(f"  Accuracy : {metriques['accuracy']:.4f}")
    logger.info(f"  F1-Score : {metriques['f1_score']:.4f}")
    logger.info(f"  AUC-ROC  : {metriques['auc_roc']:.4f}")

    # --- Sauvegardes : modele, metriques, courbe d'apprentissage, matrice de confusion ---
    repertoire_dl = REPERTOIRE_RACINE / "outputs" / "dl"
    repertoire_dl.mkdir(parents=True, exist_ok=True)

    chemin_modele = REPERTOIRE_MODELES / "deep_learning_sentiment.keras"
    modele.save(chemin_modele)
    logger.info(f"Modele sauvegarde : {chemin_modele}")

    with open(REPERTOIRE_MODELES / "deep_learning_sentiment_metadata.json", "w", encoding="utf-8") as f:
        json.dump({"nom_modele": "deep_learning_sentiment", "metriques": metriques,
                    "architecture": "Embedding + LSTM + Dense", "dataset": "IMDB (sentiment, texte)"},
                   f, indent=2, ensure_ascii=False)

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
    axes[0].plot(historique.history["accuracy"], label="Entrainement", marker="o")
    axes[0].plot(historique.history["val_accuracy"], label="Test", marker="o")
    axes[0].set_title("Accuracy au fil des epochs", fontweight="bold")
    axes[0].set_xlabel("Epoch")
    axes[0].set_ylabel("Accuracy")
    axes[0].legend()

    matrice = confusion_matrix(y_test, y_pred)
    im = axes[1].imshow(matrice, cmap="Blues")
    axes[1].set_title("Matrice de confusion (test)", fontweight="bold")
    axes[1].set_xticks([0, 1], ["Negatif predit", "Positif predit"])
    axes[1].set_yticks([0, 1], ["Negatif reel", "Positif reel"])
    for i in range(2):
        for j in range(2):
            axes[1].text(j, i, f"{matrice[i, j]}", ha="center", va="center", fontsize=13)
    plt.tight_layout()
    plt.savefig(repertoire_dl / "entrainement_et_confusion.png", dpi=200, bbox_inches="tight")
    plt.close(fig)

    # --- Demonstration lisible : un exemple decode + sa prediction ---
    # On choisit le premier exemple correctement classe (plus clair pour la demo),
    # sans cacher le taux d'erreur reel qui est donne juste au-dessus (accuracy/F1/AUC).
    index_mots = imdb.get_word_index()
    indices_corrects = np.where(y_pred == y_test)[0]
    idx_exemple = int(indices_corrects[0]) if len(indices_corrects) > 0 else 0

    exemple_texte = decoder_avis(X_test_brut[idx_exemple], index_mots)
    exemple_reel = "positive" if y_test[idx_exemple] == 1 else "negative"
    exemple_predite = "positive" if y_pred[idx_exemple] == 1 else "negative"

    logger.info("Exemple concret (une critique du jeu de test, decodee en texte lisible) :")
    logger.info(f'  Extrait : "{exemple_texte[:300]}..."')
    logger.info(f"  Sentiment reel     : {exemple_reel}")
    logger.info(f"  Sentiment predit   : {exemple_predite} (probabilite = {y_proba[idx_exemple]:.2f})")

    print("\nPreuves produites (fichiers verifiables sur disque) :")
    for chemin in [
        chemin_modele,
        REPERTOIRE_MODELES / "deep_learning_sentiment_metadata.json",
        repertoire_dl / "entrainement_et_confusion.png",
    ]:
        marque = "OK" if chemin.exists() else "MANQUANT"
        print(f"  [{marque}] {chemin.relative_to(RACINE_PROJET)}")

    print("\nBC04 termine.\n")


if __name__ == "__main__":
    main()
