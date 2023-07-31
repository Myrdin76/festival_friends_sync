from flask import render_template, request
import pandas as pd
from sqlalchemy.orm import joinedload, lazyload, aliased

from flask import render_template, redirect, url_for, flash, request, abort
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user, login_required


from app.forms import (
    LoginForm,
    RegistrationForm,
    ResetPasswordForm,
)
from app import app, db
from app.models import User, Artist, Group, user_to_group
from app.datastore import ArtistStore

# asd = ArtistStore("Lowlands")
@app.context_processor
def inject_global_params():
    """inject parameters globally

    Returns:
        dict: contains parameters that can be used across all html templates
    """

    asd = ArtistStore("Lowlands")
    artists = ["All"] + asd.get_artists()
    stages = ["All"] + asd.get_stages()
    days = ["All"] + asd.get_days()

    return dict(stages=stages, artists=artists, days=days)


@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html")


@app.route("/lineup")
def lineup():
    return render_template("lineup.html")


@app.route("/groups", methods=['GET', 'POST'])
@login_required
def groups():

    groups = Group.query.all()
    membergroups = {group.group_name: [user for user in current_user.get_friends(group.group_id)] for group in current_user.groups}
    print(membergroups)
    
    return render_template("groups.html", groups=groups, membergroups=membergroups)


@app.route("/personal_timetable")
@login_required
def personal_timetable():
    return render_template("personal_timetable.html")


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



    def get_artists_and_users_for_group(group_id):
        # Get the users who are part of the specified group
        users_in_group = User.query.filter(User.groups.any(group_id=group_id)).all()
        print("users_in_group", users_in_group)
        users_in_group = [user for user in users_in_group if user.username != current_user.username]

        # Create a dictionary to store artists and their corresponding users
        artists_and_users = {}

        # Loop through all artists
        res = current_user.get_all_artists_ordered()
        for i in range(0,len(res)):
            # Get the users who are part of the specified group and are going to this artist
            users_going_to_artist = [
                user for user in users_in_group if res[i] in user.artists
            ]
            setattr(res[i], "friendsgoing", [user.username for user in users_going_to_artist])
                
        return res
    
    res = get_artists_and_users_for_group(1)
    print(res)
    print(res[0].friendsgoing)

    return render_template("testpage.html", data=res)