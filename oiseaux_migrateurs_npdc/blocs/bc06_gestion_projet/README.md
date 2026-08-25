# BC06 — Gestion et pilotage du projet

**Objectif RNCP :** cadrer, planifier, documenter et fiabiliser un projet de science des données de
bout en bout — pas seulement écrire du code, mais aussi le rendre fiable, compréhensible et
transmissible.

Ce bloc est **autonome, y compris techniquement** : ce dossier peut être copié/envoyé seul (sans le
reste du projet) et fonctionne quand même. Il embarque pour cela sa propre copie de `acquisition.py`
(code de BC01) et de son test associé — c'est le code que ses tests vérifient.

**Changement de périmètre assumé :** dans une version précédente, ce bloc dressait aussi un "état des
lieux" vérifiant les fichiers de preuve produits par les 5 AUTRES blocs (`donnees/`, `modeles/`,
`outputs/` à la racine du projet). Cette vérification inter-blocs a été retirée : elle supposait que
tous les blocs soient présents ensemble dans la même arborescence, ce qui contredit l'autonomie totale
recherchée pour chaque dossier de bloc. Chaque bloc prouve désormais ses propres livrables
individuellement (voir la section "Livrables produits" de son propre `README.md`).

---

## Ce qui est implémenté

- Un **planning agile** sur 4 semaines, une itération par bloc de compétence.
- Une suite de **tests automatisés** (`tests/`, exécutée avec `pytest`) qui vérifie que le code
  d'acquisition (copie de BC01) fait bien ce qu'il est censé faire.
- Une liste de **limites assumées**, plutôt que cachées — la marque d'une bonne gestion de projet.

## Où le voir dans le code

- `run.py`, fonction `executer_tests` (lance `pytest` en sous-processus et affiche le résultat).
- `acquisition.py` : copie du code de BC01, testée ici.
- `tests/test_acquisition.py`, `tests/conftest.py`.

## Démonstration

```bash
cd blocs/bc06_gestion_projet
pip install -r requirements.txt
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
