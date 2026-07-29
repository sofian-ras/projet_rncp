# BC06 — Direction de projet de gestion de données

## Objectif RNCP
Piloter le projet de bout en bout, formaliser la gouvernance, et vulgariser.

## Ce livrable contient
- Cadrage problématique métier -> data
- Dossier de documentation technique et opérationnelle
- Preuves de qualité (tests)
- Plan de montée en conformité restante

## Fichier Python du livrable
- `bc06_direction_projet.py` (audit documentaire + rapport JSON)

## Preuves dans le projet
- `README.md`
- `README_COMPLET.md`
- `docs/ARCHITECTURE.md`
- `docs/PLAN_OPERATIONNEL.md`
- `GUIDE_SOUTENANCE_RNCP35288_6BLOCS.md`
- `tests/test_acquisition.py`

## Démonstration
```bash
cd oiseaux_migrateurs_npdc
python -m pytest -q
python livrables_rncp/BC06_Direction_Projet/bc06_direction_projet.py
```

## Livrables produits
- Documentation complète et soutenance argumentée
- Résultats de tests reproductibles
- `livrables_rncp/BC06_Direction_Projet/bc06_rapport_projet.json`

## Statut
- C6.1 traduction besoin: OK
- C6.5 vulgarisation: OK
- C6.6 pilotage global: OK
- C6.3 cahier des charges + budget: à formaliser dans un document dédié
- C6.4 KPI de suivi projet: à formaliser dans un tableau de bord dédié
