from flask import (Flask, abort, flash, redirect, render_template, request,
                   url_for)

from .json_handler import (load_clubs, load_competitions, save_clubs,
                           save_competitions)

app = Flask(__name__)
app.config.from_object("gudlift_reservation.config")


competitions = load_competitions()
clubs = load_clubs()
welcome_template = "welcome.html"


@app.route("/")
def index():
    """
    Affiche la page d'accueil
    """
    return render_template("index.html")


@app.route("/showSummary", methods=["POST"])
def show_summary():
    """
    Affiche le résumé des informations pour un club donné.
    Vérifie si l'email est présent et correspond à un club.
    """

    email = request.form["email"]

    if not email:
        flash("No email provided", "error")
        return redirect(url_for("index"))

    try:
        club = next(club for club in clubs if club["email"] == email)
    except StopIteration:
        flash(f"Club with this email {email} not found", "error")
        return redirect(url_for("index"))

    return render_template(welcome_template, club=club, competitions=competitions)


@app.route("/book/<competition>/<club>")
def book(competition, club):
    """
    Affiche la page de réservation pour une compétition et un club donné.
    Vérifie si la compétition et le club sont valides.
    """

    try:
        found_club = next(c for c in clubs if c["name"] == club)
    except StopIteration:
        abort(400, "Invalid club")

    try:
        found_competition = next(c for c in competitions if c["name"] == competition)
    except StopIteration:
        abort(400, "Invalid competition")

    return render_template(
        "booking.html", club=found_club, competition=found_competition
    )


@app.route("/purchasePlaces", methods=["POST"])
def purchase_places():
    """
    Gère la réservation de places pour une compétition par un club donné.
    Vérifie si la compétition et le club sont valides, puis vérifie si le club a suffisamment
    de points pour acheter des places et si le nb de places demandées est positif.
    Si le club a suffisamment de points, les places sont réservées et les points du club et les
    places de la compétition sont mis à jour.
    """

    try:
        competition = next(
            c for c in competitions if c["name"] == request.form["competition"]
        )
    except StopIteration:
        abort(400, "Invalid competition")
    try:
        club = next(c for c in clubs if c["name"] == request.form["club"])
    except StopIteration:
        abort(400, "Invalid club")

    try:
        places_required = int(request.form["places"])
        if places_required <= 0:
            flash("Number of places required must be positive", "error")
            return redirect(
                url_for("book", competition=competition["name"], club=club["name"])
            )

    except ValueError:
        flash("Invalid number", "error")
        return redirect(
            url_for("book", competition=competition["name"], club=club["name"])
        )

    if places_required <= club["points"]:

        competition["numberOfPlaces"] -= places_required
        club["points"] -= places_required

        save_clubs(clubs)
        save_competitions(competitions)

        flash("Great-booking complete!")
    else:
        flash("insufficient number of points", "error")
        return redirect(
                url_for("book", competition=competition["name"], club=club["name"])
            )

    return render_template(welcome_template, club=club, competitions=competitions)


# TODO: Add route for points display


@app.route("/logout")
def logout():
    """
    Déconnecte l'utilisateur et redirige vers la page d'accueil.
    """

    return redirect(url_for("index"))
