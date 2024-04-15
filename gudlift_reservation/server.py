import json
import os

from flask import (Flask, abort, flash, redirect, render_template, request,
                   url_for)

app = Flask(__name__)
app.config.from_object("gudlift_reservation.config")


def load_clubs():
    current_dir = os.path.dirname(__file__)
    clubs_file_path = os.path.join(current_dir, "data", "clubs.json")
    with open(clubs_file_path) as c:
        list_of_clubs = json.load(c)["clubs"]
        return list_of_clubs


def load_competitions():
    current_dir = os.path.dirname(__file__)
    competitions_file_path = os.path.join(current_dir, "data", "competitions.json")
    with open(competitions_file_path) as comps:
        list_of_competitions = json.load(comps)["competitions"]
        return list_of_competitions


competitions = load_competitions()
clubs = load_clubs()
welcome_template = "welcome.html"


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/showSummary", methods=["POST"])
def show_summary():

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

    except ValueError:
        flash("Invalid number", "error")
        return redirect(
            url_for("book", competition=competition["name"], club=club["name"])
        )

    competition["numberOfPlaces"] = int(competition["numberOfPlaces"]) - places_required
    flash("Great-booking complete!")
    return render_template(welcome_template, club=club, competitions=competitions)


# TODO: Add route for points display


@app.route("/logout")
def logout():
    return redirect(url_for("index"))
