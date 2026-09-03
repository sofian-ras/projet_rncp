# BC04 — Deep Learning (prédiction sur données non structurées)

**Objectif RNCP :** démontrer une compétence Deep Learning distincte de BC03, sur des **données non
structurées** (texte, image, son) — par opposition aux données tabulaires déjà traitées en BC03.

Ce bloc ne dépend d'aucun autre : son jeu de données (IMDB) est téléchargé par Keras au premier
lancement. Il n'utilise pas les données ornithologiques du projet (voir ci-dessous).

---

## Pourquoi un jeu de données différent du reste du projet ?

Le référentiel RNCP distingue explicitement deux compétences : BC03 porte sur des données
**structurées** (un tableau de colonnes numériques — déjà démontré sur les observations d'oiseaux), et
BC04 porte sur des données **non structurées**. Le jeu de données ornithologique de ce projet est un
tableau : il ne permet donc pas de démontrer la compétence BC04 telle qu'attendue. Le jeu **IMDB**
(25 000 critiques de films, étiquetées positif/négatif) est un choix standard, gratuit et intégré à
TensorFlow, qui permet de construire une vraie architecture de réseau de neurones sur du texte brut,
sans dépendre d'un jeu de données externe compliqué à obtenir.

## Ce qui est implémenté

- Chargement du jeu de données IMDB (critiques de films), sous-échantillonné pour un entraînement
  rapide en démonstration.
- Une architecture de réseau de neurones **Embedding + LSTM + Dense**, construite avec Keras/TensorFlow.
- Entraînement réel (5 epochs), évaluation avec Accuracy, F1-score, AUC-ROC.
- Une démonstration lisible : une critique du jeu de test est redécodée en texte, avec sa prédiction.

## Où le voir dans le code

- `modele.py`, fonction `construire_modele` (l'architecture du réseau).
- `modele.py`, fonction `decoder_avis` (retraduit les identifiants de mots en texte lisible).
- `run.py` : orchestration (chargement IMDB, split, entraînement, évaluation, sauvegardes) — la
  définition du modèle est séparée dans `modele.py`, sur le même principe que BC01 et BC03.
- Hyperparamètres dans `commun/config.py`, classe `ParametresDL`.

## Démonstration

```bash
# venv activé (cf. README racine "Démarrage rapide") — TensorFlow n'est que dans le venv
cd blocs/bc04_deep_learning
python run.py
```

Durée : environ 1 minute. **Le tout premier lancement nécessite une connexion internet** (téléchargement
unique du jeu de données IMDB, ~17 Mo, mis en cache localement) ; les lancements suivants sont
hors-ligne.

Si `python run.py` lève `ModuleNotFoundError: No module named 'tensorflow...'`, le venv n'est pas
activé ou TensorFlow n'a pas pu s'installer (limite Windows sur la longueur des chemins) — voir la
section *Dépannage : TensorFlow ne s'importe pas (BC04)* du README racine.

## Livrables produits (vérifiables sur disque)

- `modeles/deep_learning_sentiment.keras`
- `modeles/deep_learning_sentiment_metadata.json`
- `outputs/dl/entrainement_et_confusion.png`

## Statut

**Complet.** Le modèle est réellement entraîné à chaque exécution, avec de vraies métriques (Accuracy
≈ 0.83, AUC-ROC ≈ 0.92 sur l'échantillon de démonstration).
