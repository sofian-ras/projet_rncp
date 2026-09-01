# Rapport de conventions de code — Formation JEDHA / RNCP 3426

**Concepteur Développeur en Science des Données**

> Document de référence reconstruit à partir de **tout le support de cours** : démos (`Demos/`, `demos/`, `02_demos/`…),
> **corrections d'exercices**, **TP**, et surtout les **projets complets fournis en cours** (notamment
> `33. Mlflow/mlops-predictive-maintenance/` et `33. Mlflow/exercices/exercice06/correction-mlops/`,
> qui sont des projets MLOps de bout en bout servant de modèle au projet de certification).
>
> **Objectif** : servir de spécification unique à un assistant (Claude) travaillant dans le dépôt du projet de
> certification, pour qu'il aligne **la structure, le découpage et le style du code** sur ce qui est enseigné.
> Quand une « bonne pratique » du web diverge du cours, **le cours fait autorité**.

---

## SOMMAIRE

- [Partie A — Mode d'emploi pour l'assistant](#partie-a--mode-demploi-pour-lassistant)
- [Partie B — Contexte : la certification et le projet attendu](#partie-b--contexte--la-certification-et-le-projet-attendu)
- [Partie C — Sources analysées](#partie-c--sources-analysées)
- [Partie D — Conventions globales](#partie-d--conventions-globales-tout-le-code)
- [Partie E — Structure de dépôt de référence](#partie-e--structure-de-dépôt-de-référence)
- [Partie F — Conventions détaillées par couche](#partie-f--conventions-détaillées-par-couche-avec-gabarits)
  - [F1. Notebooks d'analyse & de modélisation](#f1-notebooks-danalyse--de-modélisation-ipynb)
  - [F2. `src/` — chargement & preprocessing](#f2-src--chargement--preprocessing-modules-purs)
  - [F3. `src/train.py` — entraînement + MLflow](#f3-srctrainpy--entraînement--mlflow)
  - [F4. `api/` — serving FastAPI](#f4-api--serving-fastapi)
  - [F5. `tests/` — pytest](#f5-tests--pytest)
  - [F6. Docker & docker-compose](#f6-docker--docker-compose)
  - [F7. CI/CD — GitHub Actions](#f7-cicd--github-actions)
  - [F8. Dashboards Streamlit](#f8-dashboards-streamlit-pilotage--vulgarisation)
  - [F9. Pipelines ETL (module 11)](#f9-pipelines-etl-module-11)
  - [F10. Collecte / scraping (modules 11–12)](#f10-collecte--scraping-modules-1112)
  - [F11. Spark & Spark MLlib (modules 15, 17, 24)](#f11-spark--spark-mllib-modules-15-17-24)
- [Partie G — Tableau i18n / style](#partie-g--tableau-des-règles-de-style--langue)
- [Partie H — Correspondance RNCP 3426](#partie-h--correspondance-avec-le-référentiel-rncp-3426)
- [Partie I — Checklist d'audit fichier par fichier](#partie-i--checklist-daudit-à-appliquer-au-projet)
- [Partie J — Prompt à copier](#partie-j--prompt-à-copier-dans-le-projet)

---

## PARTIE A — Mode d'emploi pour l'assistant

Tu interviens dans le dépôt d'un **projet de certification Data Science**. Ce document décrit **comment le code
est écrit en cours**. Ta mission :

1. **Auditer** le projet : pour chaque fichier / notebook, repérer les écarts par rapport à ce document,
   en citant la sous-section concernée (ex. « F4 : modèle chargé hors `lifespan` »).
2. **Proposer un plan de refactoring priorisé** (structure de dossiers d'abord, puis pipelines, API, MLflow,
   Docker, tests, CI, logging, francisation).
3. **Appliquer** les changements **fichier par fichier**, en montrant un diff après chaque fichier, **sans
   changer la logique métier ni les résultats des modèles**.

Règles impératives pendant le refactoring :

- **Langue** : commentaires, docstrings, logs, `print`, messages d'erreur, titres de graphiques → **français**.
  Le vocabulaire ML technique reste en anglais (`train_test_split`, `pipeline`, `RandomForestClassifier`…).
- **Reproductibilité** : `random_state=42` / `seed=42` **partout** (splits, modèles, SMOTE, KFold, t-SNE…).
- **Aucun** `fit_transform` manuel colonne par colonne dans un notebook de ML → toujours `Pipeline` +
  `ColumnTransformer`.
- **Séparation des responsabilités** : preprocessing dans `src/`, entraînement dans `src/train.py`,
  serving dans `api/`, jamais tout dans un seul fichier.
- **Versions figées** dans `requirements.txt`.
- Ne casse aucun test existant ; si un test manque pour du code que tu déplaces, ajoute-le (cf. F5).

Si le projet ne contient **pas encore** de structure `src/` + `api/` + `tests/`, tu proposes de la créer en
t'appuyant sur la [Partie E](#partie-e--structure-de-dépôt-de-référence).

---

## PARTIE B — Contexte : la certification et le projet attendu

**RNCP 3426** — 6 blocs de compétences :

| Bloc | Intitulé | Attendu type |
|---|---|---|
| 1 | Construction & alimentation d'une infrastructure de données | Data Lake / Warehouse, collecte web (Scrapy/BeautifulSoup), ETL, Spark/Redshift, conformité RGPD |
| 2 | Analyse exploratoire, descriptive & inférentielle | Nettoyage (NaN/aberrantes), analyses uni/multivariées, stats inférentielles, viz (Plotly/Matplotlib) pour public profane |
| 3 | Analyse prédictive — données structurées (ML) | Pipeline `scikit-learn` (encodage/normalisation/split), supervisé, non supervisé (K-Means/DBSCAN), évaluation (R²/F1, K-Fold, sur/sous-apprentissage), feature importance |
| 4 | Analyse prédictive — données non structurées (Deep Learning) | Tenseurs, augmentation, réseaux (denses/CNN/RNN), transfer learning, GAN, éval train/val, `TensorFlow` |
| 5 | Industrialisation & automatisation | MLflow + Docker (standardisation), API (FastAPI/Flask/SageMaker), appli web (Flask/Gradio/Streamlit) |
| 6 | Direction de projet data | Traduction enjeux métier → problématique data, veille, cahier des charges + rétroplanning + budget, indicateurs & tableaux de bord, vulgarisation, RGPD |

**Critères d'évaluation récurrents cités par le référentiel** (donc à respecter dans le code) :
propreté du code **PEP8** ; choix pertinent des métriques (**F1 vs recall** selon le problème,
**R²** en régression) ; **K-Fold cross-validation** ; **tests de sur-/sous-apprentissage** ;
comparaison au modèle précédent ; accessibilité pour un **public profane**.

Le projet de certification est un **projet data de A à Z** : problématique métier → data, jeu de données
justifié, jalonnement réaliste, technos justifiées, conformité RGPD, code source + soutenance.
→ La structure cible est celle d'un **projet MLOps complet** (Partie E).

---

## PARTIE C — Sources analysées

- **Python** : `03. Python bases/Demos` (15 démos), `04. Python avancé/Demos` (POO, ABC, exceptions, enum, héritage).
- **Data & ETL** : `11. ETL/02_demos` (venv, csv, pandas, openpyxl, API/JSON, **pipeline ETL POO `src/`**),
  `12. Web Scraping/02_demos` (requests robustes, BeautifulSoup, Scrapy), `13. NoSQL`, `15. ETL distribué`.
- **Analyse** : `16. Numpy et Pandas`, `19. Visualisation`, `20. Stats inférentielles/Demos`,
  `21. Analyse multivariée/demos`.
- **ML** : `23. ML supervisé/Demos` (classification, régression), `24. ML avec Spark Mllib/demos`,
  `25. Optimisation/demos` (train/test, cross-val, GridSearch, RandomSearch, courbes, ROC),
  `26. Apprentissage non supervisé/notebooks` (K-Means, DBSCAN).
- **NLP / DL** : `27. Prétraitement texte et NLP/demos` (4 notebooks), `28. Deep Learning/demos` (7 notebooks).
- **Industrialisation** : `30. API Flask FastAPI/02_demos` (Flask, FastAPI, SQLAlchemy, **`05_ml_demo_fastapi`**,
  **`babyfoot_api`**), `31. Dockerisation/demos`, `32. Déploiement/demos` + `tdd/demos` + `exercices/corrections`,
  `33. Mlflow/demos` + **`mlops-predictive-maintenance/`** + **`exercices/exercice06/correction-mlops/`**.
- **Pilotage** : `34. Agilité et gestion de projet`, `35. Indicateurs pilotage et vulgarisation/Demo`
  (dashboards Streamlit + Docker Compose), `35. .../RAG/demos`.

**Projet de référence n°1** — `33. Mlflow/mlops-predictive-maintenance/` :
`data/ · src/{preprocess,train}.py · api/{main,schemas,model_loader}.py · tests/{test_preprocess,test_model,test_api}.py ·
Dockerfile · docker-compose.yml · requirements.txt · README.md · .github/workflows/ci.yml`.
C'est le gabarit à suivre pour un projet ML industrialisé.

---

## PARTIE D — Conventions globales (tout le code)

| Sujet | Règle du cours | À corriger |
|---|---|---|
| **PEP8** | 4 espaces (**pas de tabulations**, même si certains fichiers du cours en ont), `snake_case` fonctions/variables, `PascalCase` classes, `UPPER_CASE` constantes de module. | tabs, `camelCase`, constantes en minuscule |
| **Imports** | Groupés en tête de fichier / 1ʳᵉ cellule, ordre : stdlib → tiers (numpy, pandas, sklearn…) → modules locaux (`from src.preprocess import ...`). Une ligne vide entre groupes. | imports au milieu du fichier, `import *` (sauf PySpark où le cours l'accepte) |
| **Langue** | **français** pour tout texte humain (docstrings, commentaires, logs, messages d'erreur, `print`, titres). | docstrings/messages en anglais |
| **Docstrings** | `"""Une phrase en français."""` sur chaque fonction/méthode/classe publique. Multi-lignes pour les pipelines (décrire Extract/Transform/Load ou les étapes). | fonctions publiques sans docstring |
| **Type hints** | Sur les fonctions de `src/` et `api/` : `def load_raw_data(path: str) -> pd.DataFrame:`. Facultatif dans les notebooks. | pas d'annotations dans `src/`/`api/` |
| **Constantes** | Paramètres en constantes de module en haut de fichier (`RANDOM_STATE = 42`, `DROP_COLUMNS = {...}`, `MODEL_NAME`, `TEST_SIZE`) ou `config.yaml` / `.env`. | `test_size=0.2` répété, magic numbers |
| **Chemins** | `from pathlib import Path` ; `Path(__file__).resolve().parents[1]` pour la racine projet ; `Path(...).mkdir(parents=True, exist_ok=True)` avant écriture. Jamais de chemin absolu en dur. | `open("C:/Users/...")` |
| **Point d'entrée** | Tout script exécutable finit par `if __name__ == "__main__":` appelant `main()` / `train()` / lançant le serveur. | code exécuté au niveau module |
| **Reproductibilité** | `random_state=42` / `seed=42` systématique. `np.random.seed(42)` en tête de notebook non supervisé. | absence de `random_state` |
| **Secrets** | `.env` + `python-dotenv` + `os.getenv(...)`, avec garde `if not X: raise RuntimeError(...)`. Fournir `.env.example`. `.env` dans `.gitignore`. | clé API en dur, `.env` commité |
| **Config** | `config.yaml` lu par `yaml.safe_load` **ou** variables d'environnement (`os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")`). | paramètres dispersés dans le code |
| **Gestion d'erreurs** | 3 patterns, cf. [F9](#f9-pipelines-etl-module-11) : (a) couche technique → log + `raise` ; (b) util réseau → log + `return None` ; (c) validation métier → `raise ValueError("message français explicite")`. | `except: pass`, `except Exception` muet partout |
| **Logging** | `logging` (jamais `print` pour tracer une exécution) : soit `setup_logger(name, log_file)` (ETL), soit `logging.basicConfig(level=logging.INFO); logger = logging.getLogger(__name__)` (API/scripts). Messages en français. | `print("étape 1 ok")` dans du code de prod |
| **Fichiers / nommage** | `snake_case.py`. Démos numérotées `demo01_sujet.py`. Un fichier = une responsabilité. Notebooks : `NN_sujet.ipynb`. | `Script Final (2).py`, tout dans `main.py` |
| **`.gitignore`** | `.venv/`, `__pycache__/`, `.env`, `*.pkl` volumineux, `mlruns/`, `mlflow.db`, `.pytest_cache/`, données brutes lourdes. | artefacts commités |

---

## PARTIE E — Structure de dépôt de référence

Gabarit **projet ML industrialisé** (source : `mlops-predictive-maintenance`) :

```
projet-certification/
├── data/
│   ├── raw/                 # données sources (souvent gitignore)
│   ├── processed/
│   └── output/
├── notebooks/
│   ├── 01_exploration.ipynb
│   ├── 02_modelisation.ipynb
│   └── 03_evaluation.ipynb
├── src/
│   ├── __init__.py
│   ├── preprocess.py        # fonctions pures : load_raw_data / add_engineered_features / get_feature_pipeline
│   └── train.py             # entraînement + logging MLflow + enregistrement du modèle
├── api/
│   ├── __init__.py
│   ├── main.py              # FastAPI : lifespan, /health, /metrics, /predict, /predict/batch
│   ├── schemas.py           # Pydantic : PredictionRequest / PredictionResponse
│   └── model_loader.py      # classe ModelLoader (charge depuis le MLflow Model Registry, fallback dernier run)
├── tests/
│   ├── test_preprocess.py
│   ├── test_model.py
│   └── test_api.py
├── dashboard/               # (si Bloc 6) app Streamlit de pilotage
│   └── app.py
├── .github/workflows/ci.yml # test (cov≥70) → build → security (pip-audit) → smoke (/health)
├── Dockerfile
├── docker-compose.yml       # services : mlflow / trainer (one-shot) / api  (+ dashboard)
├── requirements.txt         # versions figées
├── .env.example
├── .gitignore
└── README.md               # structure, installation, entraînement, API (endpoints), tests, docker compose
```

Variante **ETL / collecte** (Bloc 1, source : `11. ETL/.../07_demo_pipeline`) : voir [F9](#f9-pipelines-etl-module-11).
Variante **API CRUD multi-ressources** (source : `babyfoot_api`) : `app/main.py` + `app/routes/<ressource>_routes.py`
(`APIRouter(prefix=..., tags=[...])`) + `app/schemas/<ressource>.py` + `app/database.py` + `app/security.py`.

---

## PARTIE F — Conventions détaillées par couche (avec gabarits)

### F1. Notebooks d'analyse & de modélisation (`.ipynb`)

**Modules** : 16, 19, 20, 21, 23, 25, 26, 27, 28 — **Blocs 2, 3, 4**.

#### F1.1 Structure

1. **Cellule 1 = tous les imports** groupés + config + constantes :
   ```python
   import numpy as np
   import pandas as pd
   import matplotlib.pyplot as plt
   import seaborn as sns
   # ... sklearn ...

   RANDOM_STATE = 42
   np.random.seed(RANDOM_STATE)          # notebooks non supervisés
   # plt.style.use("seaborn-v0_8-darkgrid"); sns.set_palette("husl")   # accepté (module 26)
   ```
2. **Cellules markdown = titres de section** (`##`) dans l'ordre canonique :
   `Chargement des données` → `Analyse exploratoire` → `Visualisations` → `Gestion des valeurs manquantes`
   → `Sélection features / target` → `Prétraitement (Pipeline)` → `Séparation Train/Test`
   → `Entraînement` → `Optimisation des hyperparamètres` → `Évaluation du modèle`
   → `Interprétation (feature importance / SHAP)` → `Sauvegarde du modèle`.
3. **Une cellule markdown explicative avant chaque nouvel algorithme** : définition + **Avantages** / **Inconvénients**
   en listes à puces (comme `23. ML supervisé/Demos/01_demo_classification.ipynb`).
4. En non supervisé : bloc **méthode du coude + silhouette** (`for k in range(1, 11)`), tableau `k / inertie / silhouette`.

#### F1.2 Exploration + valeurs manquantes (fonction reprise du cours)

```python
def analyse_missing_data(df):
    """Renvoie les colonnes contenant des valeurs manquantes, triées par pourcentage décroissant."""
    missing = df.isnull().sum()
    missing_pct = 100 * missing / len(df)
    table = pd.DataFrame({
        "Colonnes": missing.index,
        "Valeurs manquantes": missing.values,
        "Pourcentage": missing_pct.values,
    })
    return table[table["Valeurs manquantes"] > 0].sort_values("Pourcentage", ascending=False)
```

#### F1.3 Features / target + typage automatique des colonnes

```python
features_to_keep = ["pclass", "sex", "age", "sibsp", "fare", "parch", "embarked"]
target = "survived"

X = df[features_to_keep].copy()
y = df[target].copy()

numeric_features = X.select_dtypes(include=["int64", "float64"]).columns.to_list()
categorical_features = X.select_dtypes(include=["object"]).columns.to_list()
print(f"Variables numériques : {numeric_features}")
print(f"Variables catégorielles : {categorical_features}")
```

#### F1.4 Prétraitement — **toujours `Pipeline` + `ColumnTransformer`**

```python
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer

numeric_transformer = Pipeline(steps=[
    ("imputer", SimpleImputer(strategy="median")),
    ("scaler", StandardScaler()),
])
categorical_transformer = Pipeline(steps=[
    ("imputer", SimpleImputer(strategy="constant", fill_value="missing")),
    ("onehot", OneHotEncoder(handle_unknown="ignore")),
])
preprocessor = ColumnTransformer(transformers=[
    ("num", numeric_transformer, numeric_features),
    ("cat", categorical_transformer, categorical_features),
])
```

Variante `src/` (projet mlops) : `OrdinalEncoder(categories=[["L","M","H"]], handle_unknown="use_encoded_value", unknown_value=-1)`
quand la catégorie est **ordinale**.

#### F1.5 Split

```python
from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y,   # stratify : classification uniquement
)
```

- **Classification** : `stratify=y` obligatoire ; vérifier l'équilibre (`print(f"Train : {y_train.mean():0.1%}")`).
- **Deep Learning** : split **70/15/15** (deux `train_test_split` successifs), cf. `28/demos/demo02.ipynb`.
- Scaler **`fit` sur le train seulement**, `transform` sur val/test.

#### F1.6 Entraînement = `Pipeline(preprocessor + estimateur)`

```python
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

ml_pipeline = Pipeline(steps=[
    ("preprocessor", preprocessor),
    ("classifier", RandomForestClassifier(n_estimators=100, random_state=42)),
])
ml_pipeline.fit(X_train, y_train)

print(f"Accuracy train : {accuracy_score(y_train, ml_pipeline.predict(X_train)):0.2%}")
print(f"Accuracy test  : {accuracy_score(y_test, ml_pipeline.predict(X_test)):0.2%}")   # sur/sous-apprentissage
```

Étape estimateur nommée `"classifier"` / `"regressor"` / `"clf"`. Comparaison de modèles → une `Pipeline` par modèle
(`kn_pipeline`, `dt_pipeline`, `rf_pipeline`, `voting_pipeline`).
**Données déséquilibrées** (projet mlops) : `imblearn.pipeline.Pipeline` avec `("smote", SMOTE(random_state=42))`
entre le preprocessor et le classifieur, + `class_weight="balanced"`.

#### F1.7 Optimisation d'hyperparamètres (module 25)

```python
from sklearn.model_selection import GridSearchCV

param_grid = {
    "classifier__n_estimators": [100, 200, 300],
    "classifier__max_depth": [3, 5, 10, None],
}
grid = GridSearchCV(ml_pipeline, param_grid, cv=5, scoring="f1_weighted",
                    n_jobs=-1, return_train_score=True)
grid.fit(X_train, y_train)

print(f"Meilleurs paramètres : {grid.best_params_}")
print(f"Meilleur score CV : {grid.best_score_}")
results = pd.DataFrame(grid.cv_results_).nlargest(10, "mean_test_score")
best_model = grid.best_estimator_
```

- Clés `estimateur__hyperparametre` (double underscore).
- Analyse via `DataFrame(grid.cv_results_)` + heatmap `sns.heatmap(pivot, annot=True)`.
- **K-Fold explicite** quand demandé : `StratifiedKFold(n_splits=5, shuffle=True, random_state=42)` +
  `cross_val_score(pipeline, X_train, y_train, cv=cv, scoring="f1")`.

#### F1.8 Évaluation

**Classification** — les trois sorties ensemble :
```python
from sklearn.metrics import classification_report, confusion_matrix, ConfusionMatrixDisplay

print(classification_report(y_test, y_pred, target_names=["Décédé", "Vivant"]))
disp = ConfusionMatrixDisplay(confusion_matrix=confusion_matrix(y_test, y_pred),
                              display_labels=["Décédé", "Vivant"])
disp.plot(cmap="Blues"); plt.tight_layout(); plt.show()
```
Choix de la métrique **justifié** : `recall` si les faux négatifs coûtent cher, `f1` si classes
déséquilibrées, `roc_auc` sur les probabilités (`predict_proba(X_test)[:, 1]`).

**Régression** — les quatre métriques ensemble :
```python
from sklearn.metrics import mean_absolute_error, mean_squared_error, root_mean_squared_error, r2_score
mae  = mean_absolute_error(y_test, y_pred)
mse  = mean_squared_error(y_test, y_pred)
rmse = root_mean_squared_error(y_test, y_pred)
r2   = r2_score(y_test, y_pred)
print(f"MAE : {mae}\nMSE : {mse}\nRMSE : {rmse}\nR² : {r2}")
```

**Sur-/sous-apprentissage** : comparer explicitement score train vs test, tracer les **courbes train/test**
en fonction d'un hyperparamètre (deux courbes `marker="o"`, couleurs distinctes).

#### F1.9 Non supervisé (module 26 — Bloc 3, C3.3)

```python
from sklearn.cluster import KMeans, DBSCAN
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score, davies_bouldin_score

X_scaled = StandardScaler().fit_transform(X)
kmeans = KMeans(n_clusters=4, init="k-means++", n_init=10, random_state=42)
labels = kmeans.fit_predict(X_scaled)
print(f"Inertie : {kmeans.inertia_:.2f}")
print(f"Silhouette : {silhouette_score(X_scaled, labels):.4f}")
```
- Toujours **standardiser avant** clustering.
- **Méthode du coude** (`inertia_` pour `k` de 1 à 10) **+ silhouette** pour justifier `k`.
- DBSCAN : discuter `eps` et `min_samples`. Visualiser les clusters (`scatter` coloré par label + centroïdes `marker="X"`).

#### F1.10 Deep Learning (module 28 — Bloc 4)

```python
from tensorflow import keras
from tensorflow.keras import layers

model = keras.Sequential([
    layers.Dense(64, activation="relu", input_shape=(n_features,), name="hidden_1"),
    layers.Dense(32, activation="relu", name="hidden_2"),
    layers.Dense(1, activation="linear", name="output"),
])
model.summary()
model.compile(optimizer="adam", loss="mse", metrics=["mae"])

history = model.fit(
    X_train_scaled, y_train,
    epochs=50, batch_size=64,
    validation_data=(X_val_scaled, y_val),
    verbose=1,
)
```
- Couches **nommées**, `model.summary()` systématique, **toujours** `validation_data=`.
- Tracer `history.history["loss"]` vs `["val_loss"]` (+ la métrique) en **deux subplots côte à côte**.
- Classification : `activation="softmax"` + `loss="sparse_categorical_crossentropy"` / `"binary_crossentropy"`.

#### F1.11 NLP (module 27 — Bloc 4)

Chaîne de prétraitement **dans cet ordre** : minuscules → `re.sub(r"[^a-z\s]", "", texte)` →
`.split()` → stopwords `set(stopwords.words("french"))` → lemmatisation spaCy `fr_core_news_sm`.
Vectorisation : `CountVectorizer(ngram_range=(1, 2))` / `TfidfVectorizer` **en pipeline sklearn**, ou
`Word2Vec` (`gensim`, `sg=1`, `vector_size=100`, `min_count=1`). Visualisation d'embeddings : `TSNE(random_state=42)`.

#### F1.12 Visualisation (module 19 — Bloc 2)

```python
plt.figure(figsize=(12, 5))
plt.subplot(1, 2, 1)
df["target"].value_counts().plot(kind="bar", color=["#e74c3c", "#2ecc71"])
plt.title("Distribution de la cible", fontsize=14)
plt.xlabel("target"); plt.ylabel("Nombre d'observations")
plt.xticks(rotation=0)
plt.tight_layout()
plt.show()
```
- `figsize` explicite ; `fig, axes = plt.subplots(1, n, figsize=(...))` pour les grilles ;
  titres/labels **en français** ; couleurs en hexadécimal ; **toujours** `plt.tight_layout()` puis `plt.show()`.
- `matplotlib` par défaut, `seaborn` pour le statistique, `plotly.express` pour les dashboards.

#### F1.13 Sauvegarde du modèle (notebook)

```python
import joblib
from pathlib import Path

MODEL_PATH = Path("models/model.pkl")
MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
joblib.dump(ml_pipeline, MODEL_PATH)          # la PIPELINE COMPLÈTE (preprocessing + modèle)

loaded = joblib.load(MODEL_PATH)
loaded.predict(pd.DataFrame({...}))            # entrée = DataFrame, pas un array nu
```
`joblib` + `.pkl` par défaut. `pickle` accepté côté API (`with MODEL_PATH.open("rb") as f: model = pickle.load(f)`).
En projet industrialisé, la sauvegarde « officielle » passe par **MLflow** (F3), pas par un `.pkl` local.

---

### F2. `src/` — chargement & preprocessing (modules purs)

**Source** : `mlops-predictive-maintenance/src/preprocess.py`. Principes :

- **Fonctions pures**, testables isolément, avec type hints et docstring française.
- **Ne jamais muter** le DataFrame d'entrée : `data = df.copy()` puis retour de `data`.
- Constantes de module en tête (`DROP_COLUMNS = {...}`).
- Normalisation des noms de colonnes en `snake_case` via un helper `_to_snake_case` (préfixe `_` = privé module).
- `get_feature_pipeline() -> ColumnTransformer` : **une seule fonction** renvoie le préprocesseur, réutilisée
  à l'identique par `train.py` **et** par les tests.

```python
import re
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OrdinalEncoder, StandardScaler

DROP_COLUMNS = {"udi", "product_id", "twf", "hdf", "pwf", "osf", "rnf"}


def _to_snake_case(name: str) -> str:
    """Convertit un nom de colonne quelconque en snake_case."""
    name = name.strip().replace("%", "percent")
    name = re.sub(r"[^0-9a-zA-Z]+", "_", name)
    name = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name)
    return re.sub(r"_+", "_", name).strip("_").lower()


def load_raw_data(path: str) -> pd.DataFrame:
    """Charge le CSV brut, renomme les colonnes en snake_case et retire les colonnes non pertinentes."""
    df = pd.read_csv(path)
    df = df.rename(columns={c: _to_snake_case(c) for c in df.columns})
    kept = [c for c in df.columns if c not in DROP_COLUMNS]
    return df[kept].copy()


def add_engineered_features(df: pd.DataFrame) -> pd.DataFrame:
    """Ajoute les variables dérivées métier (sans muter le DataFrame d'entrée)."""
    data = df.copy()
    data["temp_delta"] = data["process_temperature_k"] - data["air_temperature_k"]
    data["power_proxy"] = data["rotational_speed_rpm"] * data["torque_nm"]
    data["wear_per_rpm"] = data["tool_wear_min"] / (data["rotational_speed_rpm"] + 1e-6)
    return data


def get_feature_pipeline() -> ColumnTransformer:
    """Renvoie le préprocesseur (numériques standardisés, catégorielle ordinale encodée)."""
    numeric_features = [...]
    return ColumnTransformer(transformers=[
        ("num", StandardScaler(), numeric_features),
        ("cat", OrdinalEncoder(categories=[["L", "M", "H"]],
                               handle_unknown="use_encoded_value", unknown_value=-1), ["type"]),
    ])
```

---

### F3. `src/train.py` — entraînement + MLflow

**Sources** : `mlops-predictive-maintenance/src/train.py`, `33/demos/demo01`, `33/demos/demo_deploy`.

```python
import os
from pathlib import Path

import mlflow
import mlflow.sklearn
import pandas as pd
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline
from mlflow.models import infer_signature
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split

from src.preprocess import add_engineered_features, get_feature_pipeline, load_raw_data


def train() -> dict:
    """Entraîne le modèle, loggue params/métriques/modèle dans MLflow, renvoie les métriques."""
    project_root = Path(__file__).resolve().parents[1]
    data_path = project_root / "data" / "ai4i2020.csv"

    tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
    model_name = os.getenv("MODEL_NAME", "predictive-maintenance-model")
    mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_experiment("predictive-maintenance")

    df = add_engineered_features(load_raw_data(str(data_path)))
    X = df.drop(columns=["machine_failure"])
    y = df["machine_failure"]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y,
    )

    pipeline = Pipeline(steps=[
        ("preprocessor", get_feature_pipeline()),
        ("smote", SMOTE(random_state=42)),
        ("clf", RandomForestClassifier(n_estimators=300, class_weight="balanced",
                                       random_state=42, n_jobs=-1)),
    ])

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv_scores = cross_val_score(pipeline, X_train, y_train, cv=cv, scoring="f1", n_jobs=-1)

    with mlflow.start_run(run_name="rf-smote"):
        mlflow.log_params({"model_name": model_name, "n_estimators": 300,
                           "use_smote": True, "test_size": 0.2})

        pipeline.fit(X_train, y_train)
        y_pred = pipeline.predict(X_test)
        y_proba = pipeline.predict_proba(X_test)[:, 1]

        metrics = {
            "f1_score":  float(f1_score(y_test, y_pred)),
            "recall":    float(recall_score(y_test, y_pred)),
            "precision": float(precision_score(y_test, y_pred)),
            "roc_auc":   float(roc_auc_score(y_test, y_proba)),
            "cv_f1_mean": float(cv_scores.mean()),
        }
        mlflow.log_metrics(metrics)

        input_example = X_train.iloc[:5].copy()
        signature = infer_signature(input_example, pipeline.predict(input_example))
        mlflow.sklearn.log_model(
            sk_model=pipeline, artifact_path="model",
            signature=signature, input_example=input_example,
            registered_model_name=model_name,
        )
    return metrics


if __name__ == "__main__":
    print(pd.Series(train()).to_string())
```

Conventions MLflow (obligatoires) :

- `mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000"))` (ou `"sqlite:///mlflow.db"`).
- `mlflow.set_experiment("<nom-du-projet>")`.
- Tout entraînement **dans `with mlflow.start_run(run_name="...")`**, `run_name` explicite.
- `mlflow.log_params({...})` (hyperparamètres **+ `test_size`**) ; `mlflow.log_metrics({...})`
  (`f1_score`, `recall`, `precision`, `roc_auc`, `cv_f1_mean` ; ou `r2`/`rmse`/`mae` en régression).
  Convertir en `float(...)` avant de logguer.
- `mlflow.sklearn.log_model(..., artifact_path="model", signature=infer_signature(...), input_example=...,
  registered_model_name=model_name)` → enregistrement dans le **Model Registry**.
- Comparaison de plusieurs configs : liste de dicts + boucle `for i, config in enumerate(configs, 1)` avec un
  `start_run(run_name=f"config-{i}")` par itération. `mlflow.sklearn.autolog()` accepté pour `GridSearchCV`.
- `MlflowClient` pour rechercher / filtrer / taguer : `client.search_runs(experiment_ids=[...],
  filter_string="metrics.f1_score > 0.8", order_by=["metrics.f1_score DESC"])`,
  `client.set_tag(best_run_id, "status", "best_run")`.
- Promotion : `mlflow.sklearn.log_model(..., registered_model_name="x")` puis
  `client.transition_model_version_stage(name="x", version=1, stage="Production", archive_existing_versions=True)`.

---

### F4. `api/` — serving FastAPI

**Source canonique** : `mlops-predictive-maintenance/api/`. Découpage en **3 fichiers** :
`main.py` (app + routes), `schemas.py` (Pydantic), `model_loader.py` (chargement du modèle).

#### F4.1 `api/schemas.py`

```python
from typing import Literal
from pydantic import BaseModel, Field


class PredictionRequest(BaseModel):
    type: Literal["L", "M", "H"]
    air_temperature_k: float = Field(ge=250, le=400)
    process_temperature_k: float = Field(ge=250, le=450)
    rotational_speed_rpm: float = Field(ge=0, le=30000)
    torque_nm: float = Field(ge=0, le=500)
    tool_wear_min: float = Field(ge=0, le=1000)


class PredictionResponse(BaseModel):
    prediction: int
    probability: float
    risk_level: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    recommended_action: str
    model_version: str
```

- Bornes métier via `Field(ge=..., le=...)` ; énumérations via `Literal[...]` ; schéma d'entrée **séparé** du schéma de sortie.
- Validation custom : `@field_validator("champ")` + `@classmethod`, message d'erreur **en français**
  (`raise ValueError("le mot de passe doit contenir au moins une majuscule")`).
- Lecture depuis un ORM : `model_config = ConfigDict(from_attributes=True)` (Pydantic v2).

#### F4.2 `api/model_loader.py`

Classe `ModelLoader` : propriétés `is_loaded` / `version`, méthode `load()` qui **charge depuis le MLflow
Model Registry** (`models:/<name>/latest` ou `/Production` via `mlflow.pyfunc.load_model` /
`mlflow.sklearn.load_model`), avec **fallback** sur le dernier run `FINISHED` de l'expérience
(`MlflowClient().search_runs(..., order_by=["attributes.start_time DESC"], max_results=1)`).
`predict` / `predict_proba` lèvent `RuntimeError("Model not loaded")` si `_model is None`.

#### F4.3 `api/main.py`

```python
from contextlib import asynccontextmanager

import pandas as pd
from fastapi import Body, FastAPI, HTTPException

from api.model_loader import ModelLoader
from api.schemas import PredictionRequest, PredictionResponse

model_loader = ModelLoader()


def get_risk(probability: float) -> tuple[str, str]:
    """Traduit une probabilité de panne en niveau de risque + action recommandée."""
    if probability < 0.2:
        return "LOW", "Aucune action requise"
    if probability < 0.5:
        return "MEDIUM", "Planifier une inspection préventive"
    if probability < 0.75:
        return "HIGH", "Inspection dans les 24h"
    return "CRITICAL", "Arrêt immédiat recommandé"


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.metrics = {"total_predictions": 0, "failure_predictions": 0}
    try:
        model_loader.load()
    except Exception:
        pass                      # l'API démarre même sans modèle ; /health le signale
    yield


app = FastAPI(title="Predictive Maintenance API", version="1.0.0", lifespan=lifespan)


@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": model_loader.is_loaded,
            "model_version": model_loader.version}


@app.get("/metrics")
def metrics():
    total = app.state.metrics["total_predictions"]
    failures = app.state.metrics["failure_predictions"]
    return {"total_predictions": total, "failure_predictions": failures,
            "failure_rate": failures / total if total else 0.0}


@app.post("/predict", response_model=PredictionResponse)
def predict(payload: PredictionRequest):
    if not model_loader.is_loaded:
        raise HTTPException(status_code=503, detail="Model is not loaded")
    X = pd.DataFrame([payload.model_dump()])
    prediction = int(model_loader.predict(X)[0])
    probability = float(model_loader.predict_proba(X)[0][1])
    risk_level, action = get_risk(probability)
    app.state.metrics["total_predictions"] += 1
    app.state.metrics["failure_predictions"] += prediction
    return PredictionResponse(prediction=prediction, probability=probability,
                              risk_level=risk_level, recommended_action=action,
                              model_version=model_loader.version)


@app.post("/predict/batch", response_model=list[PredictionResponse])
def predict_batch(payloads: list[PredictionRequest] = Body(max_length=100)):
    if not model_loader.is_loaded:
        raise HTTPException(status_code=503, detail="Model is not loaded")
    ...
```

Conventions API :

- `FastAPI(title=..., version="1.0.0", lifespan=lifespan)`. **Chargement du modèle dans `lifespan`**, pas au
  niveau module (l'API doit démarrer même sans modèle et l'indiquer via `/health`).
- **Endpoints attendus** : `GET /health` (status + `model_loaded` + `model_version`), `GET /metrics`
  (compteurs), `POST /predict`, `POST /predict/batch` (`Body(max_length=100)`).
- Si modèle non chargé → `raise HTTPException(status_code=503, detail="...")`. Erreur applicative →
  `HTTPException(500, detail=str(e))` précédé d'un `logger.error(...)`.
- Entrée modèle = `pd.DataFrame([payload.model_dump()])` (jamais un array nu).
- Type hints partout ; réponse typée via `response_model=`.
- Lancement : `uvicorn api.main:app --host 0.0.0.0 --port 8000` (dans le `Dockerfile` / `docker-compose`), et
  bloc `if __name__ == "__main__": uvicorn.run("api.main:app", host="127.0.0.1", port=8000, reload=True)`.

#### F4.4 Variante Flask (module 30/32)

- `app = Flask(__name__)` ; routes renvoyant `jsonify({...}), <status>`.
- **Enveloppe standard** : `{"success": True, "count": n, "data": [...]}` ou `{"success": False, "error": str(e)}`.
- `try / except ValueError -> 400 / except Exception -> 500` dans chaque route.
- Découpage en couches quand le périmètre le justifie :
  `Controller (routes) → Service (règles métier, lève ValueError) → Repository (CRUD) → Model (to_dict())`.
- `app.run(host="0.0.0.0", port=5000)` (ou `7860` pour HF Spaces) sous `if __name__ == "__main__":`.

#### F4.5 Variante API CRUD multi-ressources (`babyfoot_api`)

`app/main.py` : `app.include_router(<ressource>_routes.router)`.
`app/routes/<ressource>_routes.py` : `router = APIRouter(prefix="/<ressource>", tags=["<Ressource>"])`.
`app/schemas/<ressource>.py`, `app/database.py`, `app/security.py` (hash/JWT). `.env` + `.gitignore`.

---

### F5. `tests/` — pytest

**Source** : `mlops-predictive-maintenance/tests/` + `32. Déploiement/tdd/demos`.

- **`pytest`** (jamais `unittest`). Fichiers `tests/test_<module>.py`, fonctions `test_<comportement>` en **français**
  (`test_email_sans_arobase`, `test_recall_above_threshold`).
- **Structure AAA** : Arrange / Act / Assert séparés par **une ligne vide**, un `assert` par intention.
- `@pytest.mark.parametrize("entree, attendu", [...])` pour les jeux de cas ; `@pytest.fixture` pour les données/clients partagés.
- Cycle **Rouge → Vert → Refactor**.
- **Tests de preprocessing** : forme après `fit_transform`, features numériques bien centrées (`|mean| < 1e-7`),
  encodage catégoriel correct, features dérivées justes, **pas de mutation** de l'entrée
  (`pd.testing.assert_frame_equal(original, snapshot)`).
- **Tests de modèle** : probabilités ∈ [0, 1], prédictions binaires `⊆ {0, 1}`, modèle **non trivial**
  (`len(np.unique(preds)) > 1`), **déterminisme** (`np.array_equal(preds_1, preds_2)`), **seuils de perf**
  (`recall >= 0.3`, `roc_auc >= 0.55`) sur un dataset synthétique `make_classification(..., random_state=42)`.
- **Tests d'API** : `from fastapi.testclient import TestClient` ; `FakeModelLoader` injecté via
  `monkeypatch.setattr(main, "model_loader", fake)` dans une fixture `client` ; vérifier
  `200` sur `/health` et `/predict`, **schéma de réponse** (`expected.issubset(data.keys())`),
  `probability ∈ [0, 1]`, **`422`** sur entrée invalide (`type="X"`, température hors bornes, batch > 100),
  incrément des compteurs `/metrics`.
- Objectif de **couverture ≥ 70 %** (`pytest --cov=src --cov=api --cov-report=term-missing --cov-fail-under=70`).

---

### F6. Docker & docker-compose

**Sources** : `31. Dockerisation/demos`, `32. Déploiement/demos`, `mlops-predictive-maintenance/`.

#### F6.1 Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Dépendances d'abord (cache des layers)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Puis le code
COPY . .

ENV MLFLOW_TRACKING_URI=http://mlflow:5000
ENV MODEL_NAME=predictive-maintenance-model

EXPOSE 8000
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

- **`FROM python:3.11-slim`** (ou `python:3.11.9-slim`), version figée.
- `WORKDIR /app`.
- **`COPY requirements.txt .` + `RUN pip install --no-cache-dir -r requirements.txt` AVANT `COPY . .`**.
- `ENV` pour la config (valeurs par défaut).
- `CMD ["uvicorn", ...]` pour un serveur ; `ENTRYPOINT ["python", "app.py"]` pour un script/worker ;
  `CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501"]` pour Streamlit.
- **Multi-stage** si dépendances lourdes (transformers/torch) : stage `builder` (`python -m venv /opt/venv`,
  pré-téléchargement du modèle au build), stage `runtime` (`COPY --from=builder /opt/venv /opt/venv` + cache HF).

#### F6.2 docker-compose.yml

```yaml
services:
  mlflow:
    image: ghcr.io/mlflow/mlflow:v2.13.0
    command: >
      mlflow server --host 0.0.0.0 --port 5000
      --backend-store-uri sqlite:///mlflow/mlflow.db
      --default-artifact-root /mlflow/artifacts
    ports:
      - "5000:5000"
    volumes:
      - mlflow-data:/mlflow
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:5000/health').read()"]
      interval: 10s
      timeout: 5s
      retries: 12
    networks:
      - mlops-network

  trainer:
    build: .
    command: python src/train.py
    depends_on:
      mlflow:
        condition: service_healthy
    environment:
      - MLFLOW_TRACKING_URI=http://mlflow:5000
      - MODEL_NAME=predictive-maintenance-model
    restart: "no"
    networks:
      - mlops-network

  api:
    build: .
    command: uvicorn api.main:app --host 0.0.0.0 --port 8000
    depends_on:
      mlflow:
        condition: service_healthy
    ports:
      - "8000:8000"
    environment:
      - MLFLOW_TRACKING_URI=http://mlflow:5000
      - MODEL_NAME=predictive-maintenance-model
    networks:
      - mlops-network

volumes:
  mlflow-data:

networks:
  mlops-network:
    driver: bridge
```

- 1 bloc par conteneur sous `services:` ; `build: .` **ou** `image:` (pas les deux).
- **Volumes nommés** pour la persistance ; `depends_on` + `condition: service_healthy` + `healthcheck` ;
  `environment:` en liste `- CLE=valeur` ; `trainer` = service **one-shot** (`restart: "no"`).
- Sections `volumes:` / `networks:` en bas.

---

### F7. CI/CD — GitHub Actions

**Source** : `mlops-predictive-maintenance/.github/workflows/ci.yml`. Pipeline `on: push: branches: [main]`,
4 jobs enchaînés :

1. **`test`** — `actions/setup-python@v5` (3.11) → `pip install -r requirements.txt` →
   `pytest --cov=src --cov=api --cov-report=term-missing --cov-fail-under=70`.
2. **`build`** (`needs: test`) — login GHCR, `docker/metadata-action@v5` (tags `latest` + `sha-<sha>`),
   `docker/build-push-action@v6` (`push: true`).
3. **`security`** (`needs: build`) — `pip install pip-audit` → `pip-audit -r requirements.txt`.
4. **`smoke`** (`needs: build`) — `docker build` local → `docker run -d -p 8000:8000` →
   `curl --fail http://localhost:8000/health` → cleanup `if: always()`.

---

### F8. Dashboards Streamlit (pilotage & vulgarisation)

**Source** : `35. Indicateurs pilotage et vulgarisation/Demo/Phase4-realisation/`. **Bloc 6 (C6.4, C6.5)**.

```python
import json, os, time
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

METRICS_FILE = os.getenv("METRICS_FILE", "/metrics/model_metrics.json")

st.set_page_config(page_title="KPIs de Performance Modèle", layout="wide")
st.title("KPIs de Performance Modèle")
st.caption("Simulation pédagogique : classification, régression et clustering")


def load_metrics():
    """Charge le dernier fichier de métriques ; renvoie None s'il n'existe pas encore."""
    if not os.path.exists(METRICS_FILE):
        return None
    with open(METRICS_FILE, "r") as f:
        return json.load(f)


data = load_metrics()
if data is None:
    st.warning("En attente des premières métriques...")
    time.sleep(3)
    st.rerun()

tab1, tab2, tab3 = st.tabs(["Classification", "Régression", "Vue globale"])
with tab1:
    m = data["balanced_classification"]["metrics"]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Accuracy", m["accuracy"]); c2.metric("Precision", m["precision"])
    c3.metric("Recall", m["recall"]); c4.metric("F1-score", m["f1_score"])
    fig = px.bar(pd.DataFrame([{"KPI": k, "Valeur": v} for k, v in m.items()]),
                 x="KPI", y="Valeur", range_y=[0, 1])
    st.plotly_chart(fig, use_container_width=True)

time.sleep(5)
st.rerun()
```

- `st.set_page_config(page_title=..., layout="wide")` en **première** instruction Streamlit.
- `st.title` + `st.caption`, texte **français**, orienté **public non technique**.
- KPIs = **`st.metric` dans des `st.columns(n)`** ; sections = **`st.tabs([...])`** ;
  graphes **`plotly`** (`px.bar`, `px.scatter`, `px.imshow` pour la matrice de confusion) avec
  **`use_container_width=True`**.
- Données lues depuis un **fichier JSON** (`os.getenv("METRICS_FILE", ...)`) ; rafraîchissement `time.sleep(n)` + `st.rerun()`.
- `st.warning` / `st.info` / `st.expander("Voir le JSON complet")`.
- Conteneurisé : `Dockerfile` avec `CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501"]`,
  service Compose avec volume partagé pour le JSON de métriques.
- Alternative légère : **Gradio** (`gr.Interface(fn=..., inputs=..., outputs=..., title=..., theme=gr.themes.Soft())`,
  `demo.launch()`), cf. `32. Déploiement/demos/demo_gradio`.

---

### F9. Pipelines ETL (module 11)

**Source** : `11. ETL/02_demos/07_demo_pipeline/`. **Bloc 1**.

Arborescence :

```
projet_etl/
├── config/config.yaml         # sections database / api / etl / paths
├── data/{raw,processed,output}/
├── logs/etl_api.log
├── src/
│   ├── extractors/extractors.py     # BaseExtractor(ABC) → CSVExtractor, APIExtractor
│   ├── transformers/cleaner.py      # DataTransformer : clean / validate / enrich
│   ├── loaders/loader.py            # DataLoader : load_csv / load_excel / load_multiple_sheets
│   ├── pipeline/pipeline_base.py    # ETLPipeline : run() orchestre _extract/_transform/_load
│   ├── utils/logger.py              # setup_logger(name, log_file)
│   └── pipeline_api_demo.py         # ApiDemoPipeline(ETLPipeline) : implémente les 3 étapes
└── main.py                          # load_config → setup_logger → Pipeline(config, logger).run()
```

```python
class ETLPipeline:
    """Pipeline ETL complet."""

    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.transformer = DataTransformer(logger)
        self.loader = DataLoader(logger)

    def run(self):
        """Exécute le pipeline : extraction → transformation → chargement."""
        try:
            self.logger.info("=" * 50)
            self.logger.info("DÉBUT DU PIPELINE ETL")
            data = self._extract()
            data = self._transform(data)
            self._load(data)
            self.logger.info("PIPELINE TERMINÉ AVEC SUCCÈS")
        except Exception as e:
            self.logger.error(f"PIPELINE ÉCHOUÉ: {e}")
            raise

    def _extract(self): pass
    def _transform(self, data): pass
    def _load(self, data): pass
```

- Contrat commun → classe **abstraite `ABC` + `@abstractmethod`** ; enfants appellent `super().__init__(...)`.
- Chaque méthode d'E/T/L : `try` → `self.logger.info("...")` → `return` ; `except Exception as e:` →
  `self.logger.error(f"Erreur ...: {e}")` → `raise`.
- `DataTransformer.validate(df, required_columns)` lève `ValueError(f"Colonnes manquantes: {missing}")`.
- `config.yaml` : `api.base_url / timeout / retry`, `etl.batch_size / output_format`, `paths.raw_data / processed_data / output`.
- `setup_logger` : format `%(asctime)s - %(name)s - %(levelname)s - %(message)s`, handler console **+** fichier (`encoding="utf-8"`).

---

### F10. Collecte / scraping (modules 11–12)

**Bloc 1 (C1.3), RGPD.**

```python
import requests
from requests.exceptions import RequestException, Timeout, ConnectionError

HEADERS = {"User-Agent": "My Scraper 1.0"}


def fetch_page(url, timeout=10):
    """Récupère le HTML d'une page ; renvoie None en cas d'erreur réseau/HTTP."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=timeout)
        response.raise_for_status()
        return response.text
    except Timeout:
        print(f"Timeout pour {url}")
        return None
    except ConnectionError:
        print(f"Erreur de connexion pour {url}")
        return None
    except requests.exceptions.HTTPError:
        print(f"Erreur HTTP {response.status_code}: {url}")
        return None
    except RequestException as e:
        print(f"Erreur générale: {e}")
        return None
```

- **Toujours** `timeout=` + `raise_for_status()` ; exceptions `requests` **différenciées**.
- API : clé via `.env` (`load_dotenv()` + `os.getenv`), passée en header `Authorization: Bearer ...` ou en `params`.
- Parsing : `BeautifulSoup(html, "lxml")`, `find` / `find_all` / `select`, puis
  `pd.DataFrame(rows, columns=headers)` (ou `pd.read_html(str(table))[0]`).
- Mentionner en commentaire le respect de `robots.txt` et du **RGPD** (pas de données personnelles sans base légale).
- Scrapy : structure standard `items.py` / `pipelines.py` / `middlewares.py` / `settings.py` / `spiders/`.

---

### F11. Spark & Spark MLlib (modules 15, 17, 24)

**Blocs 1, 2, 3 (traitement massif).**

```python
from pyspark.sql import SparkSession
from pyspark.ml import Pipeline, PipelineModel
from pyspark.ml.feature import Imputer, StringIndexer, OneHotEncoder, VectorAssembler, StandardScaler

spark = (SparkSession.builder
         .appName("nom_du_job")
         .master("spark://spark-master:7077")
         .getOrCreate())
spark.sparkContext.setLogLevel("WARN")

# ... construction des stages ...
train_df, test_df = df.randomSplit([0.8, 0.2], seed=42)

pipeline = Pipeline(stages=[imputer, indexer, ohe, assembler, scaler])
pipeline_model = pipeline.fit(train_df)             # fit sur TRAIN uniquement
train_prepared = pipeline_model.transform(train_df)
test_prepared = pipeline_model.transform(test_df)

pipeline_model.write().overwrite().save("/data/models/mon_pipeline")
pipeline_reload = PipelineModel.load("/data/models/mon_pipeline")

spark.stop()
```

- `SparkSession.builder` avec `.appName(...)` explicite ; `setLogLevel("WARN")`.
- **`ml.Pipeline` avec `stages=[...]`** ; `VectorAssembler(outputCol="features")` puis scaler ;
  `randomSplit([0.8, 0.2], seed=42)` ; `fit` sur train, `transform` sur les deux.
- Sauvegarde/chargement via `PipelineModel.write().overwrite().save(...)` / `.load(...)`.
- `spark.stop()` à la fin.

---

## PARTIE G — Tableau des règles de style / langue

| Élément | Convention |
|---|---|
| Docstring | `"""Phrase en français, à l'infinitif ou au présent."""` |
| Commentaire de section | `# ===== Titre =====` ou `# ----- Titre -----` |
| Message de log | `logger.info(f"...")` / `logger.error(f"Erreur ...: {e}")` — français |
| Message d'exception métier | `raise ValueError("phrase française actionnable")` |
| `print` de résultat | `print(f"Accuracy : {acc:0.2%}")` / `print(f"R² : {r2}")` |
| Titre de graphique | français, `plt.title("...", fontsize=14)` |
| Nom de fonction | `snake_case`, verbe : `load_raw_data`, `add_engineered_features`, `get_feature_pipeline` |
| Nom de test | `test_<comportement_attendu>` en français |
| Nom d'expérience MLflow | `kebab-case`, = nom du projet |
| `run_name` MLflow | descriptif : `rf-smote`, `random-forest-baseline`, `config-3` |
| Constante de module | `UPPER_SNAKE_CASE` |
| Variable ML | anglais standard : `X_train`, `y_pred`, `pipeline`, `model` |
| Variable métier | français : `donnees`, `chemin_fichier`, `resultat`, `seuil` |
| Indentation | 4 espaces, jamais de tabulation |

---

## PARTIE H — Correspondance avec le référentiel RNCP 3426

| Bloc | Compétences | Sections de ce rapport |
|---|---|---|
| **1** — Infrastructure & collecte | C1.1–C1.4 | F9 (ETL POO), F10 (collecte/scraping/RGPD), F11 (Spark), F6 (infra Docker), D (config/secrets) |
| **2** — Analyse exploratoire / stats | C2.1–C2.4 | F1.1–F1.8, F1.12 (viz), F2 (preprocessing) |
| **3** — ML prédictif (structuré) | C3.1–C3.4 | F1.4–F1.9 (Pipeline, split, GridSearch, K-Fold, éval, SHAP), F2, F3 |
| **4** — ML non structuré (DL) | C4.1–C4.5 | F1.10 (Keras), F1.11 (NLP) |
| **5** — Industrialisation | C5.1–C5.3 | F3 (MLflow), F4 (API), F5 (tests), F6 (Docker), F7 (CI/CD), F8 (Streamlit/Gradio) |
| **6** — Direction de projet | C6.1–C6.6 | F8 (dashboards), Partie B, README (Partie E), vulgarisation (Partie G), RGPD (F10) |

---

## PARTIE I — Checklist d'audit à appliquer au projet

Pour **chaque fichier / notebook** du projet, vérifier :

**Structure & organisation**
- [ ] Le dépôt suit la structure Partie E (`data/ src/ api/ tests/ notebooks/` + `Dockerfile`, `docker-compose.yml`, `requirements.txt`, `README.md`, `.env.example`, `.gitignore`, `.github/workflows/ci.yml`).
- [ ] Un fichier = une responsabilité ; pas de « tout dans `main.py` / un seul notebook ».
- [ ] `README.md` : structure, installation, entraînement, endpoints API, tests, `docker compose`.

**Style & langue (Parties D, G)**
- [ ] 4 espaces, `snake_case` / `PascalCase` / `UPPER_CASE` corrects, imports groupés en tête.
- [ ] Docstrings + commentaires + logs + messages d'erreur + titres de graphiques **en français**.
- [ ] Type hints sur `src/` et `api/`.
- [ ] `random_state=42` / `seed=42` partout ; pas de magic numbers (→ constantes ou `config`).
- [ ] Secrets via `.env` + `os.getenv` + garde ; `.env` gitignore ; `.env.example` fourni.
- [ ] `logging` au lieu de `print` dans le code non-notebook.

**Notebooks (F1)**
- [ ] Cellule 1 = imports + constantes ; sections markdown `##` dans l'ordre canonique.
- [ ] Prétraitement = `Pipeline` + `ColumnTransformer` (aucun `fit_transform` manuel colonne par colonne).
- [ ] Split avec `stratify=y` (classification) / 70-15-15 (DL) ; scaler `fit` sur train seul.
- [ ] Modèle = `Pipeline(preprocessor + estimateur)` ; comparaison train vs test affichée.
- [ ] Éval complète : `classification_report` + matrice de confusion, ou MAE/MSE/RMSE/R² ; métrique **justifiée**.
- [ ] Optimisation : `GridSearchCV` avec clés `estimateur__param` ; K-Fold explicite si pertinent.
- [ ] Non supervisé : standardisation + méthode du coude + silhouette.
- [ ] Sauvegarde de la **pipeline complète** (`joblib`/`.pkl`) ou via MLflow.

**`src/` (F2, F3)**
- [ ] `preprocess.py` : fonctions pures, `.copy()` (pas de mutation), `get_feature_pipeline()` unique et réutilisée par les tests.
- [ ] `train.py` : `set_experiment` + `with start_run(run_name=...)` + `log_params` + `log_metrics` + `log_model(..., registered_model_name=...)` + `infer_signature` + `input_example` ; `if __name__ == "__main__":`.

**`api/` (F4)**
- [ ] 3 fichiers : `main.py` / `schemas.py` / `model_loader.py` (ou package `app/` si CRUD multi-ressources).
- [ ] Modèle chargé dans `lifespan` (pas au niveau module) ; `ModelLoader` avec `is_loaded` / `version` + fallback MLflow.
- [ ] Endpoints `/health`, `/metrics`, `/predict`, `/predict/batch` ; `HTTPException(503)` si modèle absent.
- [ ] Pydantic : `Field(ge=, le=)`, `Literal[...]`, schémas entrée/sortie séparés, messages de validation français.

**`tests/` (F5)**
- [ ] `pytest`, fichiers `test_<module>.py`, noms français, structure AAA.
- [ ] Tests preprocessing (forme, centrage, encodage, non-mutation) + modèle (proba ∈ [0,1], binaire, non trivial, déterministe, seuils) + API (`TestClient` + `FakeModelLoader` via `monkeypatch`, 200 / schéma / 422).
- [ ] Couverture visée ≥ 70 %.

**Docker / CI (F6, F7)**
- [ ] `Dockerfile` : `python:3.11-slim`, `requirements` copiés/installés avant le code, `--no-cache-dir`, `ENV` de config, `CMD`/`ENTRYPOINT` adapté.
- [ ] `docker-compose.yml` : services `mlflow` / `trainer` (one-shot) / `api` (+ `dashboard`), volumes nommés, `healthcheck` + `depends_on: condition: service_healthy`, `networks`.
- [ ] `ci.yml` : jobs `test` (cov ≥ 70) → `build` → `security` (pip-audit) → `smoke` (`curl /health`).

**`requirements.txt`**
- [ ] Une entrée par dépendance, **version figée** (`==`).

---

## PARTIE J — Prompt à copier dans le projet

> À coller dans Claude Code **une fois positionné dans le dépôt du projet de certification**, avec ce fichier
> `CONVENTIONS_CODE_JEDHA.md` déposé à la racine.

```
Lis CONVENTIONS_CODE_JEDHA.md à la racine. C'est le rapport de conventions de ma
formation JEDHA (RNCP 3426), reconstruit depuis les démos ET les projets complets
fournis en cours (notamment le projet MLOps mlops-predictive-maintenance).

ÉTAPE 1 — Audit (ne modifie rien)
Applique la checklist de la Partie I à chaque fichier et notebook du projet.
Rends un tableau : fichier | écart constaté | section de référence (ex. "F4") | gravité.

ÉTAPE 2 — Plan
Propose un plan de refactoring priorisé, dans cet ordre :
structure de dossiers -> requirements figés -> src/preprocess + src/train (MLflow)
-> api/ (main/schemas/model_loader) -> tests/ -> Dockerfile + docker-compose
-> .github/workflows/ci.yml -> logging -> francisation -> notebooks.

ÉTAPE 3 — Application
Applique le plan fichier par fichier. Après CHAQUE fichier, montre le diff et attends ma validation.

Contraintes impératives :
- Ne change pas la logique métier ni les résultats/métriques des modèles.
- Français : docstrings, commentaires, logs, messages d'erreur, titres de graphiques.
- random_state=42 / seed=42 partout.
- Notebooks : Pipeline + ColumnTransformer, jamais de fit_transform manuel colonne par colonne.
- src/preprocess.py = fonctions pures sans mutation ; get_feature_pipeline() unique et réutilisée par les tests.
- src/train.py : set_experiment + with start_run(run_name=...) + log_params + log_metrics
  + log_model(registered_model_name=..., signature=infer_signature(...), input_example=...).
- api/ : modèle chargé dans lifespan, endpoints /health /metrics /predict /predict/batch, HTTPException(503) si modèle absent.
- Pydantic v2 : Field(ge=, le=), Literal[...], schémas entrée/sortie séparés.
- tests/ pytest, structure AAA, noms français, FakeModelLoader via monkeypatch, viser couverture >= 70 %.
- Dockerfile python:3.11-slim, requirements avant le code ; docker-compose services mlflow/trainer/api.
- requirements.txt : versions figées (==).
- Ne casse aucun test existant ; ajoute les tests manquants pour le code déplacé.
```
