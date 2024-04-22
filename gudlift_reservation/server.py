from flask import Flask, abort, flash, redirect, render_template, request, url_for

from .json_handler import load_clubs, load_competitions, save_clubs, save_competitions
from .utils import verif_date_in_past

app = Flask(__name__)
app.config.from_object("gudlift_reservation.config")


def load_data():
    competitions = load_competitions()
    clubs = load_clubs()
    return clubs, competitions


welcome_template = "welcome.html"


@app.route("/")
def index():
    """
    Vue pour la page d'accueil
    """
    clubs, _ = load_data()

    return render_template("index.html", clubs=clubs)


@app.route("/login")
def login():
    """
    Vue pour la page de login
    """
    return render_template("login.html")


@app.route("/showSummary", methods=["POST"])
def show_summary():
    """
    Vue pour la page welcome
    Vérifie si l'email est présent et correspond à un club.
    """
    clubs, competitions = load_data()

    email = request.form["email"]

    if not email:
        flash("No email provided", "error")
        return redirect(url_for("login"))

    try:
        club = next(club for club in clubs if club["email"] == email)
    except StopIteration:
        flash(f"Club with this email {email} not found", "error")
        return redirect(url_for("login"))

    return render_template(welcome_template, club=club, competitions=competitions)


@app.route("/book/<competition>/<club>")
def book(competition, club):
    """
    Vue pour la page de réservation pour une compétition et un club donné.
    Vérifie si la compétition et le club sont valides.
    Verifie si la date de competition n'est pas deja passée
    """
    clubs, competitions = load_data()

    try:
        found_club = next(c for c in clubs if c["name"] == club)
    except StopIteration:
        abort(400, "Invalid club")

    try:
        found_competition = next(c for c in competitions if c["name"] == competition)
    except StopIteration:
        abort(400, "Invalid competition")

    # Vérifie si la date de la compétition est déjà passée
    if verif_date_in_past(found_competition["date"]):
        flash("Competition date has already passed", "error")
        return render_template(welcome_template, club=found_club, competitions=competitions)

    return render_template("booking.html", club=found_club, competition=found_competition)


@app.route("/purchasePlaces", methods=["POST"])
def purchase_places():
    """
    Vue pour la réservation de places pour une compétition par un club donné.
    Vérifie si la compétition et le club sont valides, puis vérifie si le club a suffisamment
    de points pour acheter des places et si le nb de places demandées est positif.
    Si le club a suffisamment de points, les places sont réservées et les points du club et les
    places de la compétition sont mis à jour et les donnees sont enregistree.
    Verifie qu'un club ne reserve pas plus de 12 places par competition.
    """
    clubs, competitions = load_data()

    try:
        competition = next(c for c in competitions if c["name"] == request.form["competition"])
    except StopIteration:
        abort(400, "Invalid competition")
    try:
        club = next(c for c in clubs if c["name"] == request.form["club"])
    except StopIteration:
        abort(400, "Invalid club")

    # Vérifie si la date de la compétition est déjà passée
    if verif_date_in_past(competition["date"]):
        flash("Competition date has already passed", "error")
        return redirect(url_for("book", competition=competition["name"], club=club["name"]))

    try:
        places_required = int(request.form["places"])
        if places_required <= 0:
            flash("Number of places required must be positive", "error")
            return redirect(url_for("book", competition=competition["name"], club=club["name"]))
        elif places_required > 12:
            flash("use no more than 12 places per competition", "error")
            return redirect(url_for("book", competition=competition["name"], club=club["name"]))
        elif places_required > competition["numberOfPlaces"]:
            flash("insufficient places in the competition", "error")
            return redirect(url_for("book", competition=competition["name"], club=club["name"]))

    except ValueError:
        flash("Invalid number", "error")
        return redirect(url_for("book", competition=competition["name"], club=club["name"]))

    if places_required <= club["points"]:

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
                        flash("use no more than 12 places per competition", "error")
                        return redirect(
                            url_for(
                                "book",
                                competition=competition["name"],
                                club=club["name"],
                            )
                        )
                    entry["reserved_places"] += places_required
                    break
            else:
                competition["reserved_places"].append(reserved_places_entry)

        competition["numberOfPlaces"] -= places_required
        club["points"] -= places_required

        save_clubs(clubs)
        save_competitions(competitions)

        flash("Great-booking complete!")
    else:
        flash("insufficient number of points", "error")
        return redirect(url_for("book", competition=competition["name"], club=club["name"]))

    return render_template(welcome_template, club=club, competitions=competitions)


@app.route("/logout")
def logout():
    """
    Vue pour la page Logout
    Déconnecte l'utilisateur et redirige vers la page d'accueil.
    """

    return redirect(url_for("login"))
