from datetime import datetime


def verif_date_in_past(object_date):
    """
    Vérifie si une date est dans le passé ou non

    Args:
        object_date (date): Date à vérifier

    Returns:
        _bool_: True si la date est dans le passé.
    """
    date = datetime.strptime(object_date, "%Y-%m-%d %H:%M:%S")
    current_date = datetime.now()
    if date < current_date:
        return True
    return False
