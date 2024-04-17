import pytest

from gudlift_reservation import app
from gudlift_reservation.json_handler import (load_clubs, load_competitions,
                                              save_clubs, save_competitions)


class TestServerRoutes:
    """
    Classe de tests pour tester les routes de l'application.
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
        save_clubs(self.clubs_save)
        save_competitions(self.competitions_save)

    def test_ok_index_route(self):
        """
        Test de la route "/".
        Vérifie le code de statut de la réponse 200
        et si le contenu de la réponse contient un message spécifique.
        """
        response = self.client.get("/")
        assert response.status_code == 200
        assert b"Please enter your secretary email to continue" in response.data

    def test_ok_show_summary_route(self):
        """
        Test de la route "/showSummary".
        Envoie une requête POST avec une adresse e-mail valide
        et vérifie le code de statut de la réponse 200.
        """
        rv = self.client.post(
            "/showSummary", data=dict(email="club_test@email.fr"), follow_redirects=True
        )
        assert rv.status_code == 200

    @pytest.mark.parametrize(
        "email, expected_value",
        [
            ("", "No email provided"),
            ("fail_test@email.fr", "Club with this email fail_test@email.fr not found"),
        ],
    )
    def test_fail_show_summary_route(self, email, expected_value):
        """
        Test de la route "/showSummary".
        Envoie une requête POST avec une adresse e-mail absente ou incorrecte
        Vérifie la redirection vers index.html avec le code de statut 200 et un message d'erreur.
        """
        rv = self.client.post(
            "/showSummary", data=dict(email=email), follow_redirects=True
        )
        assert rv.status_code == 200
        assert expected_value.encode("utf-8") in rv.data

    def test_ok_book_route(self):
        """
        Test de la route "/book/<competition>/<club>" avec une competition et un club valides.
        Vérifie le code de statut de la réponse 200
        et si le contenu de la réponse contient un message spécifique.
        """
        club = "Club_test"
        competition = "Competition_test"
        response = self.client.get(f"/book/{competition}/{club}")
        assert response.status_code == 200
        assert b"How many places" in response.data

    @pytest.mark.parametrize(
        "club, competition, expected_value, status_code",
        [
            ("xxx", "Competition_test", "Invalid club", 400),
            (
                "",
                "Competition_test",
                "",
                404,
            ),
            (
                "Club_test",
                "xxx",
                "Invalid competition",
                400,
            ),
            (
                "Club_test",
                "",
                "",
                404,
            ),
        ],
    )
    def test_fail_book_route(self, club, competition, expected_value, status_code):
        """
        Test de la route "/book/<competition>/<club>" avec des données non valides.
        Vérifie le code de statut de la réponse 400 ou 404 et un message d'erreur.
        """
        response = self.client.get(f"/book/{competition}/{club}")
        assert response.status_code == status_code
        expected_value.encode("utf-8") in response.data

    def test_ok_purchase_places_route(self):
        """
        Test de la route "/purchasePlaces".
        Envoie une requête POST avec avec une competition et un club valides
        Vérifie le code de statut de la réponse 200
        et si le contenu de la réponse contient un message spécifique.
        """
        club = "Club_test"
        competition = "Competition_test"
        places = 1
        rv = self.client.post(
            "/purchasePlaces",
            data={"competition": competition, "club": club, "places": places},
        )
        assert rv.status_code == 200
        assert b"Great-booking complete!" in rv.data

    @pytest.mark.parametrize(
        "club, competition, places, expected_value, status_code",
        [
            (
                "xxx",
                "Competition_test",
                1,
                "Invalid club",
                400,
            ),
            (
                "Club_test",
                "xxx",
                1,
                "Invalid competition",
                400,
            ),
            (
                "Club_test",
                "",
                1,
                "",
                400,
            ),
            (
                "",
                "Competition_test",
                1,
                "",
                400,
            ),
            (
                "Club_test",
                "Competition_test",
                "",
                "Invalid number",
                200,
            ),
            (
                "Club_test",
                "Competition_test",
                "xxx",
                "Invalid number",
                200,
            ),
        ],
    )
    def test_fail_purchase_places_route(
        self, club, competition, places, expected_value, status_code
    ):
        """
        Test de la route "/purchasePlaces".
        Envoie une requête POST avec avec des données non valides
        Vérifie le code de statut de la réponse 400 ou 200 et un message d'erreur
        """

        rv = self.client.post(
            "/purchasePlaces",
            data={"competition": competition, "club": club, "places": places},
            follow_redirects=True,
        )
        assert rv.status_code == status_code
        assert expected_value.encode("utf-8") in rv.data

    def test_ok_logout_route(self):
        """
        Test de la route "/logout".
        Vérifie si la route renvoie un code de statut 200
        et si on est bien redirigé vers la page index.
        """
        response = self.client.get("/logout", follow_redirects=True)
        assert response.status_code == 200
        assert b"Please enter your secretary email to continue" in response.data
