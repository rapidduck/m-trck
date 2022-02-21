import json
from functools import wraps
import pywebpush
from pywebpush import webpush
from flask import Flask, render_template, url_for, request, redirect, flash, session, jsonify, send_from_directory
from flask_login import login_user, LoginManager, current_user, login_required, logout_user
from scripts.database import db, Manga, User, Subscription
from scripts.brain import Brain
from scripts.forms import *
from flask_bootstrap import Bootstrap
import os
from werkzeug.security import generate_password_hash, check_password_hash
from flask_talisman import Talisman

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db?check_same_thread=False'
app.config["SECRET_KEY"] = os.urandom(32)
# Talisman(app, content_security_policy=None)

db.app = app
db.init_app(app)
db.create_all()

bootstrap = Bootstrap(app)

login_manager = LoginManager(app)

brain = Brain(db)

@login_manager.user_loader
def get_user(user_id):
    return User.query.get(user_id)


def login_not_required(function):
    @wraps(function)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated:
            return redirect(url_for("home"))
        else:
            return function(*args, **kwargs)
    return decorated_function

@app.route("/sw.js")
def get_sw():
    return send_from_directory(".", "sw.js")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/profile")
@login_required
def show_profile():
    manga = Manga.query.join(Subscription)\
        .filter(Subscription.user_id == current_user.id)
    list_of_manga = [item.to_dict() for item in manga]
    return render_template("profile_info.html", list_of_manga=list_of_manga)


@app.route("/search")
def search():
    query = request.args.get("query")
    manga = brain.search_for_manga(query)
    return render_template("search_results.html", manga=manga, query=query)


@app.route("/manga")
def show_manga():
    url = request.args.get("query")
    details = brain.get_details(url)
    return render_template("specific_manga.html", manga=details)


@app.route("/login", methods=["POST", "GET"])
@login_not_required
def login():
    form = LoginForm()
    if form.validate_on_submit():
        entered_password = form.password.data
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None:
            if check_password_hash(user.password, entered_password):
                login_user(user)
                return redirect(url_for("show_profile"))
            else:
                flash("Your password is incorrect.")
                return redirect(url_for("login"))
        else:
            flash("This email is not registered.")
            return redirect(url_for("login"))

    return render_template("login.html", form=form, type="Log In")

@app.route("/register", methods=["POST", "GET"])
@login_not_required
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        entered_email = form.email.data
        entered_password = form.password.data

        if User.query.filter_by(email=form.email.data).first() is not None:
            flash("You are already registered, please log in!")
            return redirect(url_for("login"))
        else:
            password = generate_password_hash(entered_password, salt_length=8)

            new_user = User(
                email=entered_email,
                password=password
            )
            db.session.add(new_user)
            db.session.commit()

            login_user(new_user)
            print("Sucessfully registered the user.")
            return redirect(url_for("show_profile"))

    return render_template("login.html", form=form, type="Register")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))

@app.route("/change-password", methods=["POST", "GET"])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if check_password_hash(current_user.password, form.old_password.data):
            current_user.password = generate_password_hash(form.new_password.data, salt_length=8)
            db.session.commit()
            return redirect(url_for("show_profile"))
        else:
            flash("Your old password is incorrect.")
    return render_template("login.html", form=form, type="Change Password")


@app.route("/follow", methods=["POST"])
@login_required
def follow():
    if request.method == "POST":
        manga_arg = request.args.get("manga")
        endpoint = request.args.get("endpoint").replace("+", "%2b")
        received_manga = json.loads(manga_arg)
        endpoint = json.loads(endpoint)
        # endpoint["expirationTime"] = None

        # Checks if manga was already saved.
        manga = Manga.query.filter_by(title=received_manga["title"]).first()
        if manga is None:
            # Manga was not saved yet therefore saves it first to the db.
            manga = Manga(
                title=received_manga["title"],
                description=received_manga["description"],
                thumbnail=received_manga["thumbnail"],
                latest_chapter=received_manga["latest_chapter"],
                status=received_manga["status"],
                url=received_manga["url"]
            )
            db.session.add(manga)
            db.session.commit()

        # Add subscription to the user and the manga
        existing_endpoint = Manga.query.join(Subscription)\
            .filter(Manga.id == manga.id)\
            .filter(Subscription.endpoint == endpoint)\
            .first()

        if existing_endpoint is None:
            # Adds the users subscription to the db to the requested manga.
            new_subscription = Subscription(
                manga=manga,
                endpoint=endpoint,
                user=current_user
            )
            db.session.add(new_subscription)
            db.session.commit()
            print("Successfully saved users subscription.")
        else:
            print("Endpoint already exists.")
        return "Successfully added the subscription"

    return "Error"

@app.route("/unfollow")
@login_required
def unfollow():
    manga_id = int(request.args.get("manga_id"))
    # Find the users subscription to the manga with supplied manga_id.
    subscription = Subscription.query.join(Manga).join(User)\
        .filter(Manga.id == manga_id).filter(User.id == current_user.id).first()
    db.session.delete(subscription)

    # Remove the manga from the db if no one else follows it
    manga_subscription = Subscription.query.join(Manga).filter(Manga.id == manga_id).all()
    if len(manga_subscription) == 0:
        db.session.delete(Manga.query.get(manga_id))

    db.session.commit()
    return redirect(url_for("show_profile"))

@app.route("/notify")
def notify_all():
    manga = Manga.query.all()
    for item in manga:
        # mozna jde vymenit za item.subscriptions ale spis ne protoze to jsou children
        subscriptions = Subscription.query.join(Manga).filter(Manga.id == item.id).all()
        for subscription in subscriptions:
            try:
                webpush(subscription.endpoint,
                        json.dumps({
                            "title": item.title,
                            "body": f"New chapter {item.latest_chapter}! Go read it now!",
                        }),
                        vapid_private_key="-RMX3o_klK67WLgFA2vc6IURRwqxkUQzDkHyh4bWAEw",
                        vapid_claims={"sub": "mailto:testemail@gmail.com"})
            except pywebpush.WebPushException as e:
                print(f"Failed to push to {subscription.user.email}")
                print(e)
    return "hey hey"

if __name__ == "__main__":
    app.run()
