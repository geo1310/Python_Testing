from gudlift_reservation import app
from gudlift_reservation.json_handler import (load_clubs, load_competitions,
                                              save_clubs, save_competitions)


class TestSetup:
    """
    Configuration des tests,  création des données de tests et nettoyage aprés les tests.
    """

    @classmethod
    def setup_class(cls):
        """
        Méthode de configuration de classe exécutée une seule fois avant tous les tests.
        Initialise un client de test Flask.
        Ajoute les données de tests clubs et competitions
        Cree une sauvegarde des données initiales.
        """
        cls.client = app.test_client()
        cls.clubs = load_clubs()
        cls.competitions = load_competitions()

        # données de tests
        cls.test_clubs_data = [
            {"name": "Club_test", "email": "club_test@email.fr", "points": 15},
            {"name": "Club_test_2", "email": "club_test_2@email.fr", "points": 10},
        ]

        cls.test_competitions_data = [
            {
                "name": "Competition_test",
                "date": "2030-03-27 10:00:00",
                "numberOfPlaces": 10,
                "reserved_places": [],
            },
            {
                "name": "Competition_test_2",
                "date": "2030-03-27 10:00:00",
                "numberOfPlaces": 15,
                "reserved_places": [],
            },
        ]

        # Ajoute les données de tests
        cls.clubs.extend(cls.test_clubs_data)
        save_clubs(cls.clubs)
        cls.competitions.extend(cls.test_competitions_data)
        save_competitions(cls.competitions)

        # Crée une sauvegarde
        cls.clubs_save = load_clubs()
        cls.competitions_save = load_competitions()

    def setup_method(self):
        """
        Méthode de configuration executée au début de chaque test
        Charge les données des clubs et des compétitions.
        """
        self.clubs = load_clubs()
        self.competitions = load_competitions()

    def teardown_method(self):
        """
        Méthode de configuration executée a la fin de chaque test
        Rétablit les données de tests initiales.
        """
        save_clubs(self.clubs_save)
        save_competitions(self.competitions_save)

    @classmethod
    def teardown_class(cls):
        """
        Méthode de configuration executée a la fin de tous les tests.
        Rétablit les fichiers json d'origine, en supprimant les données de tests.
        """
        for club in cls.test_clubs_data:
            cls.clubs_save.remove(club)
        save_clubs(cls.clubs_save)

        for competition in cls.test_competitions_data:
            cls.competitions_save.remove(competition)
        save_competitions(cls.competitions_save)
