import pytest

from .. import TestSetup


class TestServerRoutes(TestSetup):
    """
    Classe de tests pour tester les routes de l'application.
    """

    def test_index_route(self):
        """
        Test de la route index "/".
        Vérifie le code de statut de la réponse 200
        et si le contenu de la réponse contient le message d'accueil.
        """
        response = self.client.get("/")
        assert response.status_code == 200
        assert b"Welcome to the GUDLFT Home page !" in response.data

    def test_login_route(self):
        """
        Test de la route "/login".
        Vérifie le code de statut de la réponse 200
        et si le contenu de la réponse contient le message de connexion.
        """
        response = self.client.get("/login")
        assert response.status_code == 200
        assert b"Welcome to the GUDLFT Registration Portal!" in response.data

    @pytest.mark.parametrize(
        "email, expected_value",
        [
            ("club_test@email.fr", "Welcome, club_test@email.fr "),  # données valides
            ("", "No email provided"),  # absence d'email
            (
                "fail_test@email.fr",
                "Club with this email fail_test@email.fr not found",
            ),  # email non valide
        ],
    )
    def test_show_summary_route(self, email, expected_value):
        """
        Test de la route "/showSummary".
        Envoie une requête POST avec une adresse e-mail valide, non valide et sans email.
        et vérifie le code de statut de la réponse 200 et un message spécifique.
        """
        rv = self.client.post("/showSummary", data=dict(email=email), follow_redirects=True)

        assert rv.status_code == 200
        assert expected_value.encode("utf-8") in rv.data

    @pytest.mark.parametrize(
        "club, competition, expected_value, status_code",
        [
            (
                "Club_test",
                "Competition_test",
                "How many places",
                200,
            ),  # données valides
            ("xxx", "Competition_test", "Invalid club", 400),  # club non valide
            (  # absence de club
                "",
                "Competition_test",
                "Not Found",
                404,
            ),
            (  # competition non valide
                "Club_test",
                "xxx",
                "Invalid competition",
                400,
            ),
            (  # absence de competition
                "Club_test",
                "",
                "Not Found",
                404,
            ),
        ],
    )
    def book_route(self, club, competition, expected_value, status_code):
        """
        Test de la route "/book/<competition>/<club>" avec des données valides et non valides.
        Vérifie le code de statut de la réponse 400 ou 404 et un message d'erreur.
        """
        response = self.client.get(f"/book/{competition}/{club}")
        assert response.status_code == status_code
        expected_value.encode("utf-8") in response.data

    @pytest.mark.parametrize(
        "club, competition, places, expected_value, status_code",
        [
            (  # données valides
                "Club_test",
                "Competition_test",
                1,
                "Great-booking complete!",
                200,
            ),
            (  # club non valide
                "xxx",
                "Competition_test",
                1,
                "Invalid club",
                400,
            ),
            (  # competition non valide
                "Club_test",
                "xxx",
                1,
                "Invalid competition",
                400,
            ),
            (  # absence de competition
                "Club_test",
                "",
                1,
                "Invalid competition",
                400,
            ),
            (  # absence de club
                "",
                "Competition_test",
                1,
                "Invalid club",
                400,
            ),
            (  # absence de places
                "Club_test",
                "Competition_test",
                "",
                "Invalid number",
                200,
            ),
            (  # places de mauvais type
                "Club_test",
                "Competition_test",
                "xxx",
                "Invalid number",
                200,
            ),
        ],
    )
    def test_purchase_places_route(self, club, competition, places, expected_value, status_code):
        """
        Test de la route "/purchasePlaces".
        Envoie une requête POST avec avec des données valides et non valides
        Vérifie le code de statut de la réponse 400 ou 200 et un message spécifique.
        """

        rv = self.client.post(
            "/purchasePlaces",
            data={"competition": competition, "club": club, "places": places},
            follow_redirects=True,
        )
        assert rv.status_code == status_code
        assert expected_value.encode("utf-8") in rv.data

    def test_logout_route(self):
        """
        Test de la route "/logout".
        Vérifie si la route renvoie un code de statut 200
        et si on est bien redirigé vers la page index.
        """
        response = self.client.get("/logout", follow_redirects=True)
        assert response.status_code == 200
        assert b"Welcome to the GUDLFT Home page !" in response.data
