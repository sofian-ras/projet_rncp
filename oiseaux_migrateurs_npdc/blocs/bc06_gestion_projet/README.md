# BC06 — Gestion et pilotage du projet

**Dépôt GitHub (tout le code du projet) :** https://github.com/sofian-ras/projet_rncp

**Objectif RNCP :** cadrer, planifier, documenter et fiabiliser un projet de science des données de
bout en bout — pas seulement écrire du code, mais aussi le rendre fiable, compréhensible et
transmissible.

Ce bloc **pilote** le projet : il exécute la suite de tests automatisés et rassemble le cadrage
(planning, risques, ROI, gouvernance). Ses tests portent sur le **vrai** module d'acquisition de
BC01 (`blocs/bc01_infrastructure_donnees/acquisition.py`), rendu importable par `tests/conftest.py`.

---

## Ce qui est implémenté

- Un **planning agile** sur 4 semaines, une itération par bloc de compétence.
- Un document de cadrage — [`docs/gestion_projet.md`](docs/gestion_projet.md) — contenant : la
  traduction de la problématique métier en problématique data, le **rétroplanning daté** avec
  jalons et dépendances, l'**analyse des risques** (probabilité / impact / mitigation / statut),
  les **coûts et bénéfices (ROI)**, et la gouvernance des données (RGPD, traçabilité,
  reproductibilité).
- Une suite de **tests automatisés** (`tests/`, exécutée avec `pytest`) qui vérifie le module
  d'acquisition de BC01 (bbox WKT, extraction des colonnes GBIF, cohérence de la config).
- Une liste de **limites assumées**, plutôt que cachées — la marque d'une bonne gestion de projet.

## Où le voir dans le code

- `run.py`, fonction `executer_tests` (lance `pytest` en sous-processus et affiche le résultat).
- `tests/test_acquisition.py` : les tests eux-mêmes.
- `tests/conftest.py` : rend importables `commun` (racine) et `acquisition` (code de BC01).

## Démonstration

```bash
pip install -r requirements.txt   # depuis la racine du projet, une seule fois
cd blocs/bc06_gestion_projet
python run.py
```

## Livrables produits

- Résultat des tests affiché en direct dans la console (6/6 tests passants).
- Planning et limites assumées affichés en console.

## Statut

**Complet.** Les tests passent, la documentation par bloc existe (un `README.md` par dossier
`blocs/bc0X_.../`), et les limites sont explicitement formulées plutôt que passées sous silence.

## Limites globales du projet, assumées

- Le modèle de BC03, bien que le meilleur des trois testés, rate encore une majorité des présences
  réelles (fort déséquilibre des classes).
- Les données GBIF reflètent l'effort d'observation humain autant que la présence réelle des oiseaux
  (biais classique des données de science citoyenne).
- Le projet est validé sur une seule région ; sa capacité à se généraliser ailleurs n'a pas été testée.
- Le déploiement cloud (API/dashboard accessibles publiquement) est documenté mais non réalisé.

## Perspectives

- Rééquilibrer les classes (SMOTE, déjà dans les dépendances) pour améliorer la détection des présences.
- Intégrer des prévisions météo (et non plus seulement de la météo passée) pour une vraie anticipation.
- Étendre le nombre d'espèces et de régions couvertes.
- Réentraîner périodiquement le modèle à mesure que de nouvelles observations GBIF sont publiées.
