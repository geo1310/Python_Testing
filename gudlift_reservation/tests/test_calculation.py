import pytest

from gudlift_reservation.json_handler import load_clubs

from . import setup_class, teardown_method


class TestCalculation:
    """
    Classe de tests pour tester les calculs de l'application.
    """

    @classmethod
    def setup_class(cls):
        setup_class(cls)

    def teardown_method(self):
        teardown_method(self)

    @pytest.mark.parametrize(
        "club_name, competition_name, places, expected_value",
        [
            ("Iron Temple", "Spring Festival", 1, "Great-booking complete!"),
            ("Iron Temple", "Spring Festival", 100, "insufficient number of points"),
            ("Iron Temple", "Spring Festival", -100, "Number of places required must be positive"),
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
            follow_redirects=True
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
