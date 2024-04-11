from gudlift_reservation import app, server


class TestServerRoutes:
    def setup_method(self):
        """
        Méthode de configuration exécutée avant chaque test.
        Initialise un client de test Flask et charge les données des clubs et des compétitions.
        """
        self.client = app.test_client()  # Initialisation du client de test Flask
        self.clubs = server.load_clubs()
        self.competitions = server.load_competitions()

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
            "/showSummary", data=dict(email="john@simplylift.co"), follow_redirects=True
        )
        assert rv.status_code == 200

    def test_fail_show_summary_route(self):
        """
        Test de la route "/showSummary".
        Envoie une requête POST avec une adresse e-mail non valide
        Vérifie le code de statut de la réponse 400 et un message d'erreur.
        """
        rv = self.client.post(
            "/showSummary", data=dict(email="test@email.fr"), follow_redirects=True
        )
        assert rv.status_code == 400
        assert b"Invalid email address" in rv.data

    def test_ok_book_route(self):
        """
        Test de la route "/book/<competition>/<club>" avec une competition et un club valides.
        Vérifie le code de statut de la réponse 200
        et si le contenu de la réponse contient un message spécifique.
        """
        club = "She Lifts"
        competition = "Spring Festival"
        response = self.client.get(f"/book/{competition}/{club}")
        assert response.status_code == 200
        assert b"How many places" in response.data

    def test_fail_book_route(self):
        """
        Test de la route "/book/<competition>/<club>" avec des données non valides.
        Vérifie le code de statut de la réponse 400 et un message d'erreur.
        """
        club = "xxx"
        competition = "xxx"
        response = self.client.get(f"/book/{competition}/{club}")
        assert response.status_code == 400
        assert b"Donnees invalides " in response.data

    def test_ok_purchase_places_route(self):
        """
        Test de la route "/purchasePlaces".
        Envoie une requête POST avec avec une competition, un club et un nb de places valides
        Vérifie le code de statut de la réponse 200
        et si le contenu de la réponse contient un message spécifique.
        """
        club = "She Lifts"
        competition = "Spring Festival"
        places = 1
        rv = self.client.post(
            "/purchasePlaces",
            data={"club": club, "competition": competition, "places": places},
        )
        assert rv.status_code == 200
        assert b"Great-booking complete!" in rv.data

    def test_fail_purchase_places_route(self):
        """
        Test de la route "/purchasePlaces".
        Envoie une requête POST avec avec des données non valides
        Vérifie le code de statut de la réponse 400 et un message d'erreur
        """
        club = "xxx"
        competition = "xxx"
        places = "xxx"
        rv = self.client.post(
            "/purchasePlaces",
            data={"club": club, "competition": competition, "places": places},
        )
        assert rv.status_code == 400
        assert b"Donnees invalides" in rv.data

    def test_ok_logout_route(self):
        """
        Test de la route "/logout".
        Vérifie si la route renvoie un code de statut 200
        et si on est bien redirigé vers la page index.
        """
        response = self.client.get("/logout", follow_redirects=True)
        assert response.status_code == 200
        assert b"Please enter your secretary email to continue" in response.data
