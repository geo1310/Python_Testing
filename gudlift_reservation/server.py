from flask import (Flask, abort, flash, redirect, render_template, request,
                   url_for)

from .json_handler import (load_clubs, load_competitions, save_clubs,
                           save_competitions)
from .utils import (reserv_places_competition, valid_club_and_competition,
                    valid_form_purchase_places, verif_date_in_past)

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

    # validation du club et de la competition
    found_club, found_competition = valid_club_and_competition(club, clubs, competition, competitions)

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
    form = request.form

    # validation du formulaire de reservation
    result_valid_form = valid_form_purchase_places(clubs, competitions, form)
    # verifie si la validation renvoie les données ou une erreur.
    if isinstance(result_valid_form, tuple):
        club, competition, places_required = result_valid_form
    else:
        return result_valid_form

    # validation de la reservation des places dans une competition
    result_reserv_places = reserv_places_competition(club, competition, places_required)
    # si la reservation s'est bien passée on enregistre les donnees
    if not result_reserv_places:
        competition["numberOfPlaces"] -= places_required
        club["points"] -= places_required
        save_clubs(clubs)
        save_competitions(competitions)
        flash("Great-booking complete!")
    else:
        return result_reserv_places

    return render_template(welcome_template, club=club, competitions=competitions)


@app.route("/logout")
def logout():
    """
    Vue pour la page Logout
    Déconnecte l'utilisateur et redirige vers la page d'accueil.
    """

    return redirect(url_for("index"))
