from flask import render_template, request
import pandas as pd

from flask import render_template, redirect, url_for, flash, request, abort
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user, login_required


from app.forms import (
    LoginForm,
    RegistrationForm,
    ResetPasswordForm,
)
from app import app, db
from app.models import User, Artist, Group
from app.datastore import ArtistStore

# asd = ArtistStore("Lowlands")
with app.app_context():

    @app.context_processor
    def inject_global_params():
        """inject parameters globally

        Returns:
            dict: contains parameters that can be used across all html templates
        """

        asd = ArtistStore("Lowlands")
        artists = ["All"] + asd.artists
        stages = ["All"] + asd.stages
        days = ["All"] + asd.days

        return dict(stages=stages, artists=artists, days=days)


@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html")


@app.route("/lineup")
def lineup():
    return render_template("lineup.html")


@app.route("/groups", methods=['GET', 'POST'])
def groups():

    groups = Group.query.all()
    membergroups = current_user.groups
    
    return render_template("groups.html", groups=groups, membergroups=membergroups)

@app.route("/personal_timetable")
def personal_timetable():
    data = current_user.get_all_artists_ordered()
 
    return render_template("personal_timetable.html", data=data)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash(('Invalid username or password'))
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title=('Sign In'), form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(('All good, lets go!'))
        return redirect(url_for('login'))
    return render_template('register.html', title=('Register'), form=form)


@app.route("/testpage")
def testpage():
    return render_template("testpage.html")