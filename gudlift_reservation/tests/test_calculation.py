from datetime import datetime, timedelta

import pytest

from gudlift_reservation.json_handler import load_clubs, load_competitions, save_competitions

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
        "club_name, competition_name, places, expected_value",
        [
            (  # donnees valides
                "Club_test",
                "Competition_test_2",
                5,
                "Great-booking complete!",
            ),
            (  # nombre de places > 12
                "Club_test",
                "Competition_test_2",
                13,
                "use no more than 12 places per competition",
            ),
        ],
    )
    def test_competition_reserved_places(self, club_name, competition_name, places, expected_value):
        """
        Verifie la réservation des places dans une compétition
        Les places reservées doivent etre enregistrées dans le champ reserved_places de la compétition.
        Le nombre de places réservées dans ne doit pas dépasser 12 par competition.
        """

        rv = self.client.post(
            "/purchasePlaces",
            data={"competition": competition_name, "club": club_name, "places": places},
            follow_redirects=True,
        )

        # verification des places reservées par le club dans reserved_places de la competition
        self.competitions = load_competitions()
        self.competition = next(comp for comp in self.competitions if comp["name"] == competition_name)
        if "Great-booking complete!" in expected_value:
            reserved_places = self.competition["reserved_places"][0]["reserved_places"]
            assert reserved_places == places
            assert reserved_places <= 12

        assert rv.status_code == 200
        assert expected_value.encode("utf-8") in rv.data

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
