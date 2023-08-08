from flask import render_template, request, session
import pandas as pd
from sqlalchemy.orm import joinedload, lazyload, aliased

from flask import render_template, redirect, url_for, flash, request, abort
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user, login_required


from app.forms import (
    LoginForm,
    RegistrationForm,
    ResetPasswordForm,
    EmptyForm,
    ChangeUsernameForm
)
from app import app, db
from app.models import User, Artist, Group, user_to_group, GroupInvite
from app.datastore import ArtistStore
from app.wrappers import membership_required
from app.helpers import create_group_invite_link

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
    groups = Group.query.filter(Group.private != True).all()
    membergroups = {group.group_name: [user for user in current_user.get_friends(group.group_id)] for group in current_user.groups}
    print(membergroups)
    
    return render_template("groups.html", groups=groups, membergroups=membergroups)


@app.route("/personal_timetable")
@login_required
def personal_timetable():
    print(len(current_user.groups))
    if len(current_user.groups) > 0:
        has_groups = True
    else:
        has_groups = False
    return render_template("personal_timetable.html", has_groups=has_groups)


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
        if invite_token := session.get('group_invite_token'):
            print("session_invite_token", invite_token)
            session.pop('group_invite_token', None)
            return redirect(url_for('accept_invite_link', invite_token=invite_token))
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
        
        # Initial group invite
        gadd = GroupInvite(to_group_id=2, from_user_id=8, to_user_id=user.user_id)
        db.session.add(gadd)
        db.session.commit()
        flash(('All good, lets go!'))
        return redirect(url_for('login'))
    return render_template('register.html', title=('Register'), form=form)

@app.route('/user')
@login_required
def user():
    cu_form = ChangeUsernameForm()
    return render_template('user.html', cu_form=cu_form)


@app.route('/group/<int:group_id>')
@login_required
@membership_required
def group(group_id):
    group = Group.query.get(group_id)
    friends = current_user.get_friends(group_id)
    invite_url = create_group_invite_link(group_id)
    return render_template('group.html', group=group, friends=friends, invite_url=invite_url)


@app.route("/testpage")
def testpage():
    # tst
    return render_template("testpage.html")