from datetime import datetime, timedelta

import pytest

from gudlift_reservation import app
from gudlift_reservation.json_handler import (load_clubs, load_competitions,
                                              save_clubs, save_competitions)


class TestCalculation:
    """
    Classe de tests pour tester les calculs de l'application.
    """

    @classmethod
    def setup_class(cls):
        """
        Méthode de configuration de classe exécutée une seule fois avant tous les tests.
        Initialise un client de test Flask
        Charge les données des clubs et des compétitions.
        Cree des sauvegardes de clubs.json et competitions.json
        """
        cls.client = app.test_client()
        cls.clubs = load_clubs()
        cls.competitions = load_competitions()
        cls.clubs_save = load_clubs()
        cls.competitions_save = load_competitions()

    def teardown_method(self):
        """
        Méthode de configuration executée a la fin des tests
        Rétablit les fichiers json d'origine.
        """
        self.clubs = self.clubs_save
        self.competitions = self.competitions_save
        save_clubs(self.clubs_save)
        save_competitions(self.competitions_save)

    @pytest.mark.parametrize(
        "club_name, competition_name, places, expected_value",
        [
            ("Club_test", "Competition_test", 10, "Great-booking complete!"),
            ("Club_test_2", "Competition_test_2", 11, "insufficient number of points"),
            (
                "Club_test",
                "Competition_test",
                -100,
                "Number of places required must be positive",
            ),
        ],
    )
    def test_club_purchase_places_calculation(
        self, club_name, competition_name, places, expected_value
    ):
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

        self.clubs = load_clubs()
        club = next(club for club in self.clubs if club["name"] == club_name)
        club_points_after = club["points"]
        expected_points = club_points_before - places

        assert rv.status_code == 200
        assert expected_value.encode("utf-8") in rv.data
        assert club_points_after >= 0

        if expected_value == "Great-booking complete!":
            assert club_points_after == expected_points

    @pytest.mark.parametrize(
        "club_name, competition_name, places, expected_value",
        [
            (
                "Club_test_2",
                "Competition_test",
                13,
                "use no more than 12 places per competition",
            ),
        ],
    )
    def test_competition_no_more_12_places(
        self, club_name, competition_name, places, expected_value
    ):
        """
        Verifie l'utilisation des places d'une compétition
        Le nombre de place utilisé par un club doit etre de 12 maximum pour une competition.
        """

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
            ("Club_test", "Competition_test", 1, "Great-booking complete!"),
        ],
    )
    def test_competition_reserved_places(
        self, club_name, competition_name, places, expected_value
    ):
        """
        Verifie la réservation des places dans une compétition
        Les places reservées doivent etre enregistrées dans le champ reserved_places de la compétition.
        Le nombre de places réservées ne doit pas dépasser 12.
        """

        rv = self.client.post(
            "/purchasePlaces",
            data={"competition": competition_name, "club": club_name, "places": places},
            follow_redirects=True,
        )

        assert rv.status_code == 200
        assert expected_value.encode("utf-8") in rv.data

        # TODO ajouter verif dans reserved_places

    def test_date_competition_not_be_in_past(self):
        """
        Vérifie qu'on ne peut pas réserver de places dans une compétition deja passée.
        """
        self.competition = next(
            comp for comp in self.competitions if comp["name"] == "Competition_test"
        )

        date_test = datetime.now() - timedelta(days=50)
        self.competition["date"] = date_test.strftime("%Y-%m-%d %H:%M:%S")
        save_competitions(self.competitions)

        self.competitions = load_competitions()

        response = self.client.get("/book/Competition_test/Club_test")

        assert response.status_code == 200
        assert b"Competition date has already passed" in response.data

    @pytest.mark.parametrize(
        "club_name, competition_name, places, expected_value",
        [
            (
                "Club_test",
                "Competition_test",
                12,
                "insufficient places in the competition",
            ),
        ],
    )
    def test_competition_available_places(
        self, club_name, competition_name, places, expected_value
    ):
        """
        Verifie si le nombre de places dans une competition est suffisant
        Il ne peut pas etre négatif.
        """

        rv = self.client.post(
            "/purchasePlaces",
            data={"competition": competition_name, "club": club_name, "places": places},
            follow_redirects=True,
        )

        assert rv.status_code == 200
        assert expected_value.encode("utf-8") in rv.data
