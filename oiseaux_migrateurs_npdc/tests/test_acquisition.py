"""
Tests unitaires - BC01 Acquisition
"""

import pytest
from pathlib import Path
import pandas as pd
import numpy as np

from scripts.config import ESPECES, ZONE_GEOGRAPHIQUE, ParametresAcquisition
from scripts.acquisition import AcquisiteurGBIF


class TestAcquisiteurGBIF:
    """Tests pour acquisition GBIF"""
    
    def test_creation_bbox(self):
        """Test creation bounding box WKT"""
        acquisiteur = AcquisiteurGBIF()
        bbox = acquisiteur._creer_bbox_geometrie()
        
        # Verifier format WKT
        assert bbox.startswith("POLYGON")
        assert "(" in bbox
        assert bbox.count(",") >= 4  # Au minimum 4 coordonnees
    
    def test_extraction_colonnes(self):
        """Test extraction colonnes depuis reponse GBIF"""
        observations_mock = [
            {
                "scientificName": "Barn Swallow",
                "eventDate": "2023-05-15",
                "decimalLatitude": 50.5,
                "decimalLongitude": 2.75,
                "coordinateUncertaintyInMeters": 100,
                "country": "FR",
                "gbifID": 123456,
            }
        ]
        
        resultat = AcquisiteurGBIF._extraire_colonnes(
            observations_mock,
            "hirondelle_rustique"
        )
        
        assert len(resultat) == 1
        assert resultat[0]["espece"] == "hirondelle_rustique"
        assert resultat[0]["latitude"] == 50.5
        assert resultat[0]["longitude"] == 2.75


class TestConfigurationEspeces:
    """Tests configuration especes"""
    
    def test_especes_definies(self):
        """Verifie especes definies"""
        assert len(ESPECES) == 4
        assert "hirondelle_rustique" in ESPECES
        assert "cigogne_blanche" in ESPECES
    
    def test_structure_espece(self):
        """Verifie structure donnees espece"""
        for nom, infos in ESPECES.items():
            assert "nom_francais" in infos
            assert "nom_scientifique" in infos
            assert "code_gbif" in infos
            assert "mois_arrivee" in infos
            assert "mois_depart" in infos


class TestZoneGeographique:
    """Tests zone geographique"""
    
    def test_zone_valide(self):
        """Verifie coordonnees zone NPDC"""
        zone = ZONE_GEOGRAPHIQUE
        
        assert zone.latitude_min < zone.latitude_max
        assert zone.longitude_min < zone.longitude_max
        assert zone.nom_region == "Nord-Pas-de-Calais"
    
    def test_centre_dans_zone(self):
        """Verifie centre dans zone"""
        zone = ZONE_GEOGRAPHIQUE
        
        assert zone.latitude_min <= zone.centre_latitude <= zone.latitude_max
        assert zone.longitude_min <= zone.centre_longitude <= zone.longitude_max


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
