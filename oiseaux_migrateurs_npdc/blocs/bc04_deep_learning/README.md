# BC04 — Deep Learning (prédiction sur données non structurées)

**Objectif RNCP :** démontrer une compétence Deep Learning distincte de BC03, sur des **données non
structurées** (texte, image, son) — par opposition aux données tabulaires de BC03 — avec une
architecture de réseau conçue, entraînée, évaluée, et **une analyse d'explicabilité**.

Ce bloc propose **deux démonstrations** :

| Version | Données | Modèle | Fichiers |
|---|---|---|---|
| **Images** (dans le thème du projet) | photos GBIF des **4 espèces** du projet | CNN — *transfer learning* MobileNetV2 + Grad-CAM | `notebook_bc04_images.ipynb`, `acquisition_images.py` |
| **Texte** (repli léger, 100 % hors-ligne) | jeu **IMDB** (critiques de films) | Embedding + LSTM + Dense | `notebook_bc04.ipynb`, `run.py`, `modele.py` |

La version **images** est la démonstration principale : elle reste sur le sujet ornithologique du
projet et couvre l'explicabilité (Grad-CAM). La version **texte** est conservée parce qu'elle est
figée, rapide et reproductible sans dépendre d'un téléchargement d'images (utile si le réseau est
indisponible le jour de la démo).

---

## Version images — reconnaître l'espèce sur une photo

### Ce qui est implémenté

- **Acquisition** de ~120 photos par espèce depuis **GBIF** (`mediaType=StillImage` : iNaturalist /
  Flickr), mises en cache dans `donnees/images_oiseaux/` (`acquisition_images.py`).
- **Chargement** avec `image_dataset_from_directory` (redimensionnement 160×160, split 80/20).
- **Data augmentation** (`RandomFlip`, `RandomRotation`, `RandomZoom`, `RandomContrast`).
- **Transfer learning** : `MobileNetV2` pré-entraîné sur ImageNet, **gelé**, + tête
  `GlobalAveragePooling2D → Dropout → Dense(4, softmax)`. Seuls ~5 000 paramètres sont entraînés.
- **Entraînement** (10 epochs, ~1–2 min sur CPU) + courbes loss / accuracy.
- **Évaluation** : accuracy de validation + **matrice de confusion** 4×4.
- **Explicabilité** : **Grad-CAM** — visualise les zones de la photo qui pèsent le plus dans la
  décision (« où le modèle regarde »).

### Où le voir dans le code

- `notebook_bc04_images.ipynb` : le pipeline déroulé **de haut en bas, façon cours** (récupérer les
  photos → charger → augmentation → transfer learning → entraînement → confusion → prédictions →
  Grad-CAM), chaque section expliquée avant le code, interprétée après.
- `acquisition_images.py`, fonction `telecharger_images` : requête GBIF + téléchargement en cache.

### Démonstration

```bash
# venv activé (cf. README racine) ; ouvrir notebook_bc04_images.ipynb
```

Le **tout premier lancement nécessite une connexion internet** (téléchargement des photos, ~450 Mo
pour 480 images, puis en cache ; + poids de MobileNetV2, ~10 Mo, cache Keras). Résultat typique :
**accuracy de validation ≈ 0,74** (hasard = 0,25 pour 4 classes), sur des photos de science
citoyenne volontairement bruitées.

---

## Version texte — analyse de sentiment (IMDB)

### Pourquoi un jeu de données différent du reste du projet ?

Le référentiel distingue BC03 (données **structurées** — déjà démontré sur les observations
d'oiseaux) et BC04 (données **non structurées**). Le jeu **IMDB** (25 000 critiques de films,
étiquetées positif/négatif), intégré à TensorFlow, permet de construire un vrai réseau sur du
**texte brut** sans dépendre d'un téléchargement d'images : c'est la version de repli, figée et
reproductible.

### Ce qui est implémenté

- Chargement IMDB (sous-échantillonné pour un entraînement rapide).
- Architecture **Embedding + LSTM + Dense**.
- Entraînement réel (5 epochs), évaluation Accuracy / F1-score / AUC-ROC.
- Démonstration lisible : une critique du jeu de test redécodée en texte, avec sa prédiction.

### Où le voir dans le code

- `notebook_bc04.ipynb` : pipeline à plat (chargement → décodage d'une critique → `pad_sequences`
  → `Embedding + LSTM + Dense` → entraînement → courbes → confusion → prédictions).
- `modele.py`, `construire_modele` (l'architecture) et `decoder_avis` (numéros de mots → texte).
- `run.py` : la même chose en une commande.
- Hyperparamètres dans `commun/config.py`, classe `ParametresDL`.

### Démonstration

```bash
# venv activé
python blocs/bc04_deep_learning/run.py
```

Durée ~1 minute. Premier lancement : téléchargement unique d'IMDB (~17 Mo), ensuite hors-ligne.
Si `ModuleNotFoundError: No module named 'tensorflow...'` : venv non activé ou TensorFlow non
installé — voir *Dépannage* du README racine.

### Livrables produits

- `modeles/deep_learning_sentiment.keras`, `modeles/deep_learning_sentiment_metadata.json`
- `outputs/dl/entrainement_et_confusion.png`
- Métriques : Accuracy ≈ 0,83, AUC-ROC ≈ 0,92 sur l'échantillon de démonstration.

---

## Statut

**Complet.** Deux réseaux réellement entraînés à chaque exécution : un CNN (transfer learning) sur
images d'oiseaux avec explicabilité Grad-CAM, et un Embedding + LSTM sur texte. Limites assumées :
photos de science citoyenne bruitées et dataset volontairement petit côté images ; jeu générique
(IMDB) côté texte.
