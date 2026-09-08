"""
BC04 - Architecture du reseau : transfer learning MobileNetV2 pour classer
une photo d'oiseau parmi les 4 especes du projet.

Separe de run.py (orchestration) pour ne pas melanger la definition du
modele et le pipeline d'entrainement.
"""

from commun.config import ParametresDL


def construire_modele(nb_classes: int, taille_image: int = ParametresDL.TAILLE_IMAGE):
    """Construit le modele (MobileNetV2 gele + tete Dense) et son jumeau pour Grad-CAM.

    Retourne (modele, modele_gradcam) :
      - modele         : entree image -> probabilite par espece
      - modele_gradcam : entree image -> (derniere carte de convolution, probabilites),
                         necessaire pour l'explicabilite Grad-CAM.
    """
    from tensorflow import keras
    from tensorflow.keras import layers

    # Data augmentation : appliquee seulement a l'entrainement (cree des variantes
    # des photos pour eviter le sur-apprentissage avec peu d'images).
    augmentation = keras.Sequential([
        layers.RandomFlip("horizontal"),
        layers.RandomRotation(0.10),
        layers.RandomZoom(0.10),
        layers.RandomContrast(0.10),
    ], name="augmentation")

    # Corps pre-entraine sur ImageNet, GELE : seule la tete apprendra.
    base = keras.applications.MobileNetV2(
        input_shape=(taille_image, taille_image, 3), include_top=False, weights="imagenet"
    )
    base.trainable = False

    entree = keras.Input((taille_image, taille_image, 3))
    x = augmentation(entree)
    x = layers.Rescaling(1.0 / 127.5, offset=-1)(x)          # pixels [0,255] -> [-1,1] (format MobileNetV2)
    caracteristiques = base(x, training=False)                # derniere carte de convolution : 5 x 5 x 1280
    x = layers.GlobalAveragePooling2D()(caracteristiques)
    x = layers.Dropout(ParametresDL.DROPOUT_RATE)(x)
    sortie = layers.Dense(nb_classes, activation="softmax")(x)

    modele = keras.Model(entree, sortie, name="oiseaux_mobilenetv2")
    modele_gradcam = keras.Model(entree, [caracteristiques, sortie])
    modele.compile(optimizer="adam", loss="sparse_categorical_crossentropy", metrics=["accuracy"])
    return modele, modele_gradcam
