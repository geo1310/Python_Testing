import json
import os


def load_data(file_name):
    """
    Charge les données à partir d'un fichier JSON.

    Args:
        file_name (str): Le nom du fichier JSON.

    Returns:
        dict: Les données chargées depuis le fichier JSON.
    """
    current_dir = os.path.dirname(__file__)
    file_path = os.path.join(current_dir, "data", file_name)
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_data(data, file_name):
    """
    Enregistre les données dans un fichier JSON.

    Args:
        data (dict): Les données à enregistrer.
        file_name (str): Le nom du fichier JSON où enregistrer les données.
    """
    current_dir = os.path.dirname(__file__)
    file_path = os.path.join(current_dir, "data", file_name)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f)


def load_clubs():
    """
    Retourne la liste des clubs de clubs.json
    """
    return load_data("clubs.json")["clubs"]


def load_competitions():
    """
    Retourne la liste des competitions de competitions.json
    """
    return load_data("competitions.json")["competitions"]


def save_clubs(clubs):
    """
    Sauvegarde la liste des clubs en argument dans clubs.json
    """
    save_data({"clubs": clubs}, "clubs.json")


def save_competitions(competitions):
    """
    Sauvegarde la liste des competitions en argument dans competitions.json
    """
    save_data({"competitions": competitions}, "competitions.json")
