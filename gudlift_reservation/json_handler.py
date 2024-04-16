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
    with open(file_path) as f:
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
    with open(file_path, "w") as f:
        json.dump(data, f)


def load_clubs():
    return load_data("clubs.json")["clubs"]


def load_competitions():
    return load_data("competitions.json")["competitions"]


def save_clubs(clubs):
    save_data({"clubs": clubs}, "clubs.json")


def save_competitions(competitions):
    save_data({"competitions": competitions}, "competitions.json")
