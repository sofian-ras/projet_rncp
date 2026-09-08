"""
BC04 - Deep Learning : prediction sur donnees NON structurees (images)
======================================================================

Classe une photo d'oiseau parmi les 4 especes du projet, avec un CNN en
transfer learning : MobileNetV2 pre-entraine sur ImageNet, corps gele,
seule une petite tete de classification est entrainee.

  1. Acquisition : ~120 photos par espece depuis GBIF (mediaType=StillImage).
  2. Chargement en jeux entrainement / validation (image_dataset_from_directory).
  3. Modele : data augmentation -> MobileNetV2 gele -> tete Dense(4).
  4. Entrainement, evaluation (accuracy + matrice de confusion), sauvegarde.
  5. Explicabilite : Grad-CAM sur quelques photos ("ou le modele regarde").

Utilisation :
    python blocs/bc04_deep_learning/run.py

Le premier lancement telecharge les photos (connexion internet requise, mises
en cache dans donnees/images_oiseaux/) ainsi que les poids de MobileNetV2 ;
les lancements suivants sont hors-ligne.
"""

import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

_racine = next(p for p in Path(__file__).resolve().parents if (p / "commun").is_dir())
sys.path.insert(0, str(_racine))                      # -> package commun/
sys.path.insert(0, str(Path(__file__).resolve().parent))  # -> acquisition_images, modele

from commun.config import REPERTOIRE_MODELES, REPERTOIRE_RACINE, ParametresDL
from commun.journalisation import configurer_logger
from acquisition_images import telecharger_images, REPERTOIRE_IMAGES
from modele import construire_modele

logger = configurer_logger()


def _grad_cam(modele_gradcam, image):
    """Carte de chaleur Grad-CAM (redimensionnee a la taille de l'image) + classe predite."""
    import tensorflow as tf

    lot = image[None, ...]
    with tf.GradientTape() as tape:
        cartes, predictions = modele_gradcam(lot)
        classe = tf.argmax(predictions[0])
        score = predictions[:, classe]
    gradients = tape.gradient(score, cartes)
    poids = tf.reduce_mean(gradients, axis=(0, 1, 2))
    chaleur = tf.reduce_sum(cartes[0] * poids, axis=-1)
    chaleur = tf.maximum(chaleur, 0) / (tf.reduce_max(chaleur) + 1e-8)
    chaleur = tf.image.resize(chaleur[..., None], lot.shape[1:3]).numpy().squeeze()
    return chaleur, int(classe)


def main() -> None:
    print("\n" + "#" * 70)
    print("# BC04 - DEEP LEARNING (donnees non structurees : images)")
    print("#" * 70 + "\n")

    logger.info("Chargement de TensorFlow/Keras (peut prendre quelques secondes)...")
    import tensorflow as tf
    from tensorflow import keras
    from sklearn.metrics import accuracy_score, confusion_matrix, f1_score

    tf.random.set_seed(ParametresDL.RANDOM_STATE)

    # 1. Acquisition des photos (skip si deja en cache)
    telecharger_images(ParametresDL.NB_IMAGES_PAR_ESPECE)

    # 2. Jeux d'entrainement / validation
    parametres_ds = dict(
        validation_split=ParametresDL.VALIDATION_SPLIT,
        seed=ParametresDL.RANDOM_STATE,
        image_size=(ParametresDL.TAILLE_IMAGE, ParametresDL.TAILLE_IMAGE),
        batch_size=ParametresDL.BATCH_SIZE,
    )
    train_ds = keras.utils.image_dataset_from_directory(REPERTOIRE_IMAGES, subset="training", **parametres_ds)
    val_ds = keras.utils.image_dataset_from_directory(REPERTOIRE_IMAGES, subset="validation", **parametres_ds)
    noms_classes = train_ds.class_names
    logger.info(f"Classes : {noms_classes}")

    autotune = tf.data.AUTOTUNE
    train_ds = train_ds.cache().shuffle(500).prefetch(autotune)
    val_ds = val_ds.cache().prefetch(autotune)

    # 3. Modele : transfer learning MobileNetV2
    logger.info("Construction du modele (MobileNetV2 gele + tete Dense)...")
    modele, modele_gradcam = construire_modele(len(noms_classes))
    modele.summary()

    # 4. Entrainement
    logger.info(f"Entrainement ({ParametresDL.EPOCHS} epochs)...")
    historique = modele.fit(train_ds, validation_data=val_ds, epochs=ParametresDL.EPOCHS, verbose=2)

    # Evaluation sur la validation
    y_vrai = np.concatenate([y.numpy() for _, y in val_ds])
    y_proba = modele.predict(val_ds, verbose=0)
    y_pred = y_proba.argmax(axis=1)
    metriques = {
        "accuracy": float(accuracy_score(y_vrai, y_pred)),
        "f1_macro": float(f1_score(y_vrai, y_pred, average="macro")),
    }
    logger.info(f"  Accuracy validation : {metriques['accuracy']:.4f}")
    logger.info(f"  F1-macro            : {metriques['f1_macro']:.4f}")

    # --- Sauvegardes : modele, metriques, courbes + confusion, Grad-CAM ---
    repertoire_dl = REPERTOIRE_RACINE / "outputs" / "dl"
    repertoire_dl.mkdir(parents=True, exist_ok=True)

    chemin_modele = REPERTOIRE_MODELES / "deep_learning_oiseaux.keras"
    modele.save(chemin_modele)
    logger.info(f"Modele sauvegarde : {chemin_modele}")
    with open(REPERTOIRE_MODELES / "deep_learning_oiseaux_metadata.json", "w", encoding="utf-8") as f:
        json.dump({
            "nom_modele": "deep_learning_oiseaux",
            "metriques": metriques,
            "architecture": "MobileNetV2 (transfer learning, corps gele) + Dense",
            "classes": noms_classes,
            "dataset": "photos GBIF (4 especes du projet)",
        }, f, indent=2, ensure_ascii=False)

    n = len(noms_classes)
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.5))
    axes[0].plot(historique.history["accuracy"], marker="o", label="entrainement")
    axes[0].plot(historique.history["val_accuracy"], marker="o", label="validation")
    axes[0].axhline(1 / n, color="gray", linestyle="--", label=f"hasard ({n} classes)")
    axes[0].set_title("Accuracy au fil des epochs", fontweight="bold")
    axes[0].set_xlabel("epoch"); axes[0].legend()

    cm = confusion_matrix(y_vrai, y_pred)
    axes[1].imshow(cm, cmap="Blues")
    axes[1].set_title("Matrice de confusion (validation)", fontweight="bold")
    axes[1].set_xticks(range(n)); axes[1].set_xticklabels(noms_classes, rotation=45, ha="right")
    axes[1].set_yticks(range(n)); axes[1].set_yticklabels(noms_classes)
    for i in range(n):
        for j in range(n):
            axes[1].text(j, i, cm[i, j], ha="center", va="center")
    plt.tight_layout()
    plt.savefig(repertoire_dl / "entrainement_et_confusion.png", dpi=150, bbox_inches="tight")
    plt.close(fig)

    # Grad-CAM sur 4 photos de validation
    images, _ = next(iter(val_ds))
    fig, axes = plt.subplots(2, 4, figsize=(14, 7))
    for k in range(4):
        chaleur, classe = _grad_cam(modele_gradcam, images[k])
        photo = tf.cast(images[k], tf.uint8).numpy()
        axes[0, k].imshow(photo); axes[0, k].axis("off")
        axes[0, k].set_title(f"predit : {noms_classes[classe]}", fontsize=9)
        axes[1, k].imshow(photo); axes[1, k].imshow(chaleur, cmap="jet", alpha=0.45)
        axes[1, k].axis("off")
    plt.suptitle("Grad-CAM : ou le modele regarde", fontweight="bold")
    plt.tight_layout()
    plt.savefig(repertoire_dl / "grad_cam.png", dpi=150, bbox_inches="tight")
    plt.close(fig)

    print("\nExemple : une photo du jeu de validation, sa prediction.")
    chaleur, classe = _grad_cam(modele_gradcam, images[0])
    logger.info(f"  Espece predite : {noms_classes[classe]}")

    print("\nPreuves produites (fichiers verifiables sur disque) :")
    for chemin in [
        chemin_modele,
        REPERTOIRE_MODELES / "deep_learning_oiseaux_metadata.json",
        repertoire_dl / "entrainement_et_confusion.png",
        repertoire_dl / "grad_cam.png",
    ]:
        marque = "OK" if chemin.exists() else "MANQUANT"
        print(f"  [{marque}] {chemin.relative_to(REPERTOIRE_RACINE)}")

    print("\nBC04 termine.\n")


if __name__ == "__main__":
    main()
