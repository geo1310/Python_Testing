from datetime import datetime

from flask import abort, request


def verif_date_in_past(object_date):
    """
    Vérifie si une date est dans le passé ou non.

    Renvoie True si la date est dans le passé.

    """
    date = datetime.strptime(object_date, "%Y-%m-%d %H:%M:%S")
    current_date = datetime.now()
    if date < current_date:
        return True
    return False


def valid_club_and_competition(club_name, clubs, competition_name, competitions):
    """
    Valide si les noms du club et de la competition fournis sont valides.

    Renvoie le club et la competition trouvés dans la base ou un abort avec une erreur.
    """

    try:
        found_club = next(c for c in clubs if c["name"] == club_name)
    except StopIteration:
        abort(400, "Invalid club")

    try:
        found_competition = next(c for c in competitions if c["name"] == competition_name)
    except StopIteration:
        abort(400, "Invalid competition")

    return found_club, found_competition


def reserv_places_competition(club, competition, places_required):
    """
    Réserve les places dans une compétition et crée ou complète le champ reserved_places
    Vérifie que le nombre de place réservées par club ne dépasse pas 12

    Renvoie True ou False si la reservation ne s'est pas bien passée.
    """

    if places_required > 12:
        return False

    reserved_places_entry = {
        "club_name": club["name"],
        "reserved_places": places_required,
    }

    if not competition["reserved_places"]:
        competition["reserved_places"].append(reserved_places_entry)
    else:
        for entry in competition["reserved_places"]:

            if entry["club_name"] == club["name"]:
                if entry["reserved_places"] + places_required > 12:
                    return False
                entry["reserved_places"] += places_required
                break
        else:
            competition["reserved_places"].append(reserved_places_entry)
    return True


def valid_form_purchase_places(clubs, competitions, form):
    """
    Validation du formulaire pour la reservation de places dans une competition.
    Verifie si le club et la competition sont valides.
    Verifie si la date de competition n'est pas passée.
    Verifie si le nombre de places demandées est valide.

    Si aucunes erreurs :Renvoie True et une liste avec le club, la competition et les places demandées.
    Si erreurs trouvées :Renvoie False et une liste avec le club, la competition et le message d'erreur
    """
    # validation du club et de la competition
    club, competition = valid_club_and_competition(form["club"], clubs, form["competition"], competitions)

    # Vérifie si la date de la compétition est déjà passée
    if verif_date_in_past(competition["date"]):
        return False, [club, competition, "Competition date has already passed", "error"]

    try:
        places_required = int(request.form["places"])
        if places_required <= 0:
            return False, [club, competition, "Number of places required must be positive", "error"]

        elif places_required > competition["numberOfPlaces"]:
            return False, [club, competition, "insufficient places in the competition", "error"]
        elif places_required > club["points"]:
            return False, [club, competition, "insufficient number of points", "error"]

        return True, [club, competition, places_required]

    except ValueError:
        return False, [club, competition, "Invalid number", "error"]
