from datetime import datetime, timedelta

import pytest

from gudlift_reservation.json_handler import (load_clubs, load_competitions,
                                              save_competitions)
from gudlift_reservation.utils import (reserv_places_competition,
                                       valid_club_and_competition)

from . import TestSetup


class TestCalculation(TestSetup):
    """
    Classe de tests pour tester les calculs de l'application.
    """

    @pytest.mark.parametrize(
        "club_name, competition_name, places, expected_value",
        [
            (  # donnees valides
                "Club_test",
                "Competition_test",
                10,
                "Great-booking complete!",
            ),
            (  # nombre de places supérieur au points du club
                "Club_test_2",
                "Competition_test_2",
                11,
                "insufficient number of points",
            ),
            (  # nombre de places negatif
                "Club_test",
                "Competition_test",
                -100,
                "Number of places required must be positive",
            ),
            (  # nombre de places superieures à 12
                "Club_test",
                "Competition_test_2",
                13,
                "use no more than 12 places per competition",
            ),
        ],
    )
    def test_club_purchase_places_calculation(self, club_name, competition_name, places, expected_value):
        """
        Verifie l'utilisation des points d'un club.
        Le nombre de points demandés doit etre positif.
        Les points du club doivent rester positif ou nul.
        Les points utilisés doivent etre déduits des points du club.
        """

        club = next(club for club in self.clubs if club["name"] == club_name)
        club_points_before = club["points"]

        rv = self.client.post(
            "/purchasePlaces",
            data={"competition": competition_name, "club": club_name, "places": places},
            follow_redirects=True,
        )

        assert rv.status_code == 200
        assert expected_value.encode("utf-8") in rv.data

        # verification du bon calcul des points du club
        if expected_value == "Great-booking complete!":
            self.clubs = load_clubs()
            club = next(club for club in self.clubs if club["name"] == club_name)
            club_points_after = club["points"]
            expected_points = club_points_before - places

            assert club_points_after == expected_points
            assert club_points_after >= 0

    @pytest.mark.parametrize(
        "club_name, competition_name, expected_value",
        [
            ("Club_test", "Competition_test", "Competition date has already passed"),
        ],
    )
    def test_book_date_competition_not_be_in_past(self, club_name, competition_name, expected_value):
        """
        Vérifie qu'on ne peut pas réserver de places dans une compétition deja passée.
        Dans la méthode GET de de la route de réservation book
        """
        self.competition = next(comp for comp in self.competitions if comp["name"] == competition_name)

        # modification de la date de la competition
        date_test = datetime.now() - timedelta(days=50)
        self.competition["date"] = date_test.strftime("%Y-%m-%d %H:%M:%S")
        save_competitions(self.competitions)

        response = self.client.get(f"/book/{competition_name}/{club_name}")

        assert response.status_code == 200
        assert expected_value.encode("utf-8") in response.data

    @pytest.mark.parametrize(
        "club_name, competition_name, places, expected_value",
        [
            ("Club_test", "Competition_test", 1, "Competition date has already passed"),
        ],
    )
    def test_purchase_places_date_competition_not_be_in_past(
        self, club_name, competition_name, places, expected_value
    ):
        """
        Vérifie qu'on ne peut pas réserver de places dans une compétition deja passée.
        Dans la méthode POST de de la route purchase_places
        """
        self.competition = next(comp for comp in self.competitions if comp["name"] == competition_name)

        # modification de la date de la competition
        date_test = datetime.now() - timedelta(days=50)
        self.competition["date"] = date_test.strftime("%Y-%m-%d %H:%M:%S")
        save_competitions(self.competitions)

        self.competitions = load_competitions()

        rv = self.client.post(
            "/purchasePlaces",
            data={"competition": competition_name, "club": club_name, "places": places},
            follow_redirects=True,
        )

        assert rv.status_code == 200
        assert expected_value.encode("utf-8") in rv.data

    @pytest.mark.parametrize(
        "club_name, competition_name, places, expected_value",
        [
            (  # nombre de places superieur au places disponibles de la competition
                "Club_test",
                "Competition_test",
                12,
                "insufficient places in the competition",
            ),
        ],
    )
    def test_competition_available_places(self, club_name, competition_name, places, expected_value):
        """
        Verifie si le nombre de places dans une competition est suffisant.
        Il ne peut pas etre négatif.
        """

        rv = self.client.post(
            "/purchasePlaces",
            data={"competition": competition_name, "club": club_name, "places": places},
            follow_redirects=True,
        )

        assert rv.status_code == 200
        assert expected_value.encode("utf-8") in rv.data

    @pytest.mark.parametrize(
        "club_name, competition_name, places",
        [
            (  # nombre de places à valider 3 fois
                "Club_test",
                "Competition_test",
                5,
            ),
        ],
    )
    def test_reserved_places_competition(self, club_name, competition_name, places):
        """
        Test de la fonction reserved_places_competition.
        Vérifie que le nombre de places réservées par un club ne peut pas dépasser 12
        par compétition dans reserved_places de la compétition.
        """

        found_club, found_competition = valid_club_and_competition(
            club_name, self.clubs, competition_name, self.competitions
        )

        # 1-demande initiale de n places
        result = reserv_places_competition(found_club, found_competition, places)
        assert result == True
        assert found_competition["reserved_places"][0]["club_name"] == found_club["name"]
        reserved_places_1 = found_competition["reserved_places"][0]["reserved_places"]
        assert reserved_places_1 <= 12
        assert reserved_places_1 == places

        # 2-demande de n places
        result = reserv_places_competition(found_club, found_competition, places)
        assert result == True
        reserved_places_2 = found_competition["reserved_places"][0]["reserved_places"]
        assert reserved_places_2 <= 12
        assert reserved_places_2 == reserved_places_1 + places

        # 3-demande de n places ( résultat > 12 )
        result = reserv_places_competition(found_club, found_competition, places)
        assert result == False

        # test avec un autre club
        found_club, _ = valid_club_and_competition("Club_test_2", self.clubs, competition_name, self.competitions)
        result = reserv_places_competition(found_club, found_competition, places)
        assert result == True
