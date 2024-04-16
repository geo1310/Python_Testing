from gudlift_reservation import app, server
from gudlift_reservation.json_handler import save_clubs, save_competitions


def setup_class(cls):
    """
    Méthode de configuration de classe exécutée une seule fois avant tous les tests.
    Initialise un client de test Flask
    Charge les données des clubs et des compétitions.
    Cree des sauvegardes de clubs.json et competitions.json
    """
    cls.client = app.test_client()
    cls.clubs = server.load_clubs()
    cls.competitions = server.load_competitions()
    cls.clubs_save = cls.clubs
    cls.competitions_save = cls.competitions


def teardown_method(self):
    """
    Méthode de configuration executée a la fin des tests
    Rétablit les fichiers json d'origine.
    """
    save_clubs(self.clubs_save)
    save_competitions(self.competitions_save)
