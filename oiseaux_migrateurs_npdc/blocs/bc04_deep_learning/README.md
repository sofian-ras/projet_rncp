# BC04 — Deep Learning : reconnaissance d'espèce sur photo

**Objectif RNCP :** démontrer une compétence Deep Learning distincte de BC03, sur des **données non
structurées** (ici des **images**), avec une architecture de réseau conçue, entraînée, évaluée, et
**une analyse d'explicabilité**.

On reste dans le **thème du projet** : un réseau de neurones convolutif (CNN) apprend à regarder une
photo et à dire **laquelle des 4 espèces** du projet elle montre — Hirondelle rustique, Cigogne
blanche, Martinet noir, Bergeronnette.

---

## Ce qui est implémenté

- **Acquisition** de ~120 photos par espèce depuis **GBIF** (`mediaType=StillImage` : observations
  iNaturalist / Flickr, URL JPEG directes), mises en cache dans `donnees/images_oiseaux/`
  (`acquisition_images.py`).
- **Chargement** avec `image_dataset_from_directory` (redimensionnement 160×160, split 80/20).
- **Data augmentation** (`RandomFlip`, `RandomRotation`, `RandomZoom`, `RandomContrast`) — crée des
  variantes des photos pour éviter le sur-apprentissage avec peu d'images.
- **Transfer learning** : `MobileNetV2` pré-entraîné sur ImageNet, **corps gelé**, + tête
  `GlobalAveragePooling2D → Dropout → Dense(4, softmax)`. Seuls ~5 000 paramètres sont entraînés.
- **Entraînement** (10 epochs, ~1–2 min sur CPU) + courbes loss / accuracy.
- **Évaluation** : accuracy de validation + **matrice de confusion** 4×4.
- **Explicabilité — Grad-CAM** : visualise les zones de la photo qui pèsent le plus dans la
  décision (« où le modèle regarde »).

## Où le voir dans le code

- `notebook_bc04.ipynb` : le pipeline déroulé **de haut en bas, façon cours** (récupérer les photos
  → charger → augmentation → transfer learning → entraînement → confusion → prédictions → Grad-CAM),
  chaque section expliquée avant le code, interprétée après. Version pour l'explication orale.
- `acquisition_images.py`, `telecharger_images` : requête GBIF + téléchargement en cache.
- `modele.py`, `construire_modele` : l'architecture (MobileNetV2 gelé + tête), et son jumeau exposant
  la dernière carte de convolution pour le Grad-CAM.
- `run.py` : la même chose en une commande (acquisition → datasets → modèle → entraînement →
  évaluation → sauvegardes).
- Hyperparamètres dans `commun/config.py`, classe `ParametresDL`.

## Démonstration

```bash
# venv activé (cf. README racine "Démarrage rapide") — TensorFlow n'est que dans le venv
python blocs/bc04_deep_learning/run.py
```

Le **tout premier lancement nécessite une connexion internet** : téléchargement des photos
(~450 Mo pour 480 images, puis en cache dans `donnees/images_oiseaux/`) et des poids de MobileNetV2
(~10 Mo, cache Keras). Les lancements suivants sont hors-ligne.

Si `python run.py` lève `ModuleNotFoundError: No module named 'tensorflow...'`, le venv n'est pas
activé ou TensorFlow n'a pas pu s'installer (limite Windows sur la longueur des chemins) — voir la
section *Dépannage : TensorFlow ne s'importe pas (BC04)* du README racine.

## Livrables produits (vérifiables sur disque)

- `modeles/deep_learning_oiseaux.keras`
- `modeles/deep_learning_oiseaux_metadata.json`
- `outputs/dl/entrainement_et_confusion.png`
- `outputs/dl/grad_cam.png`

## Statut

**Complet.** Le CNN est réellement entraîné à chaque exécution. Résultat typique : **accuracy de
validation ≈ 0,75** (hasard = 0,25 pour 4 classes), sur des photos de science citoyenne
volontairement bruitées (oiseau lointain, de dos, plusieurs individus, nids).

**Limites assumées :** dataset volontairement petit (~120 photos/espèce) ; les données GBIF
reflètent aussi l'effort d'observation ; un *fine-tuning* du corps MobileNetV2 (dégeler les
dernières couches) gagnerait quelques points d'accuracy.
