import pytest
from flask import session

from gudlift_reservation.json_handler import (load_clubs, load_competitions,
                                              save_competitions)

from .. import TestSetup


class TestIntegrationApp(TestSetup):
    """
    Classe de tests d'intégration de l'application
    """

    @pytest.mark.parametrize(
        "email, club_name, competition_name, places, status_code_1, status_code_2",
        [
            ("club_test@email.fr", "Club_test", "Competition_test", 10, 200, 200),  # donnees valides
            ("club_test@email.fr", "Club_test", "Competition_test", 100, 200, 302),  # données non valides
        ],
    )
    def test_user_workflow(self, email, club_name, competition_name, places, status_code_1, status_code_2):
        """
        Test un parcours utilisateur avec le login, la réservation de places et le logout
        """
        # login utilisateur
        with self.client:
            response = self.client.post("/showSummary", data={"email": email})

            assert response.status_code == status_code_1

            # vérifie la session utilisateur
            if status_code_1 == 200:
                assert session.get("user_id") == email
            else:
                assert session.get("user_id") is None

        # réserve de places
        with self.client:

            # données avant la requete
            club = next(club for club in self.clubs if club["name"] == club_name)
            competition = next(comp for comp in self.competitions if comp["name"] == competition_name)
            club_points_before = club["points"]
            competition_places_before = competition["numberOfPlaces"]

            response = self.client.post(
                "/purchasePlaces", data={"club": club_name, "competition": competition_name, "places": places}
            )
            assert response.status_code == status_code_2
            assert session.get("user_id") == email

            # données apres la requete
            self.clubs = load_clubs()
            self.competitions = load_competitions()
            club = next(club for club in self.clubs if club["name"] == club_name)
            competition = next(comp for comp in self.competitions if comp["name"] == competition_name)

            # vérifie la modification des données
            if status_code_2 == 200:
                assert club["points"] == club_points_before - places
                assert competition["numberOfPlaces"] == competition_places_before - places
            else:
                assert club["points"] == club_points_before
                assert competition["numberOfPlaces"] == competition_places_before

        # logout utilisateur
        with self.client:
            response = self.client.get("/logout")
            assert response.status_code == 302
            assert session.get("user_id") is None
