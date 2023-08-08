from flask import render_template, request, jsonify, redirect, url_for, make_response, flash, session, Markup
from flask_login import login_required, current_user
import pandas as pd

from app import app, db
from app.models import User, Artist, Group, GroupInvite
from app.forms import ChangeUsernameForm, EmptyForm, CreateGroupForm
from sqlalchemy import select, func, text
from app.helpers import verify_group_invite_token
# from app.datastore import ArtistStore

@app.route('/api/fill_table')
def fill_table():
    stage = request.args.get('stageselector')
    day = request.args.get('dayselector')
    if stage == 'All' and day == 'All':
        where_stmt = ""
    elif stage == 'All':
        where_stmt = "WHERE day = :day"
    elif day == 'All':
        where_stmt = "WHERE stage = :stage"
    else:
        where_stmt = "WHERE stage = :stage AND day = :day"
    
    txt = f"""
            SELECT artist.*, COALESCE(B.user_id, 0) as user_going
            FROM artist 
            LEFT JOIN (
                SELECT *
                FROM user_to_artist
                WHERE user_to_artist.user_id = :user_id
                ) as B ON
                artist.artist_id = B.artist_id
            {where_stmt}
        """
    user_id = current_user.user_id if current_user.is_authenticated else 0
    stmt = text(txt)
    data = db.session.execute(stmt, {"user_id": user_id, "stage":stage, "day":day}).fetchall()
        
    return render_template('api/fill_table.html', data=data)

@app.route('/api/delete_artist/<int:artist_id>', methods=['GET', 'POST'])
@login_required
def delete_artist(artist_id):
    current_user.remove_user_from_artist(Artist.query.get(int(artist_id)))
    return ""


@app.get('/api/select_artist')
@login_required
def select_artist():    
    res = request.args.lists()
    # Access all values in the ImmutableMultiDict
    for key, value_list in res:
        artist_id = key
        enable = True if value_list[0] == 'on' else False
    
    print(artist_id, enable)
    
    if enable:
        current_user.add_user_to_artist(Artist.query.get(artist_id))
    else:
        current_user.remove_user_from_artist(Artist.query.get(artist_id))

    return ""



@app.route('/api/join_group', methods=['GET', 'POST'])
@login_required
def join_group():
    gid = request.args.get('groupselector')
    group = Group.query.get(gid)
    current_user.add_user_to_group(group)
    
    return render_template('api/list_of_groups.html')


@app.route('/api/leave_group', methods=['GET', 'POST'])
@login_required
def leave_group():
    gid = request.args.get('groupselector')
    group = Group.query.get(gid)
    current_user.remove_user_from_group(group)
    
    return render_template('api/list_of_groups.html')

@app.route('/api/get_groups', methods=['GET'])
@login_required
def get_groups():
    return render_template('api/list_of_groups.html')


# @app.route('/api/get_friends')
# @login_required
# def get_friends():
#     gid = request.args.get('groupselector')
#     group = Group.query.get(gid)
    
#     return render_template('api/list_of_friends.html')


@app.route('/api/fill_personal')
@login_required
def fill_personal():
    res = current_user.get_all_artists_ordered()
    group_id = request.args.get('groupselector')
    
    if group_id is None or group_id == '' or len(group_id) == 0:
        pass
    else:
        # Get the users who are part of the specified group
        users_in_group = User.query.filter(User.groups.any(group_id=group_id)).all()
        users_in_group = [user for user in users_in_group if user.username != current_user.username]
    
        for i in range(0,len(res)):
            # Get the users who are part of the specified group and are going to this artist
            users_going_to_artist = [
                user for user in users_in_group if res[i] in user.artists
            ]
            setattr(res[i], "friendsgoing", [user.username for user in users_going_to_artist])
    
    return render_template('api/fill_personal.html', data=res)

@app.route('/api/change_username', methods=['GET', 'POST'])
@login_required
def change_username():
    if request.method == 'POST':
        form = ChangeUsernameForm(request.form)
        if form.validate_on_submit():
            name = form.username.data
            current_user.username = name
            db.session.commit()
            
            response = make_response(f"<p>Username: <b>{name}</b></p>")
            response.headers['HX-Trigger'] = "clear_form"
            return response
        else:
            response = make_response("Invalid username")
            response.headers['HX-Retarget'] = "#validation_error"
            return response
    else:
        cu_form = ChangeUsernameForm()
        return render_template("api/change_username_form.html", cu_form=cu_form)


@app.route('/api/get_open_invites')
def get_open_invites():
    invites = current_user.get_open_invites()
    if len(invites) == 0:
        return "<p> <i>Currently you do not have any open invites </i> </p>"
    return render_template('api/open_invites.html', invites=invites)

@app.route('/api/accept_invite/<int:invite_id>')
def accept_invite(invite_id):
    current_user.accept_group_invite(invite_id)
    response = make_response("<p> <em> Invite accepted 🎉 🤘</em> </p>")
    response.headers['HX-Trigger'] = "reloadg"
    
    return response

@app.route('/api/decline_invite/<int:invite_id>')
def decline_invite(invite_id):
    gi = GroupInvite.query.get(invite_id)
    db.session.delete(gi)
    db.session.commit()
    return "<p> <em> Invite declined ☹️ ⚡️ </em> </p> "


@app.route('/api/invite_user/<int:user_id>', methods=['GET', 'POST'])
def invite_user(user_id):
    if request.method == "POST":
        to_group_id = int(request.form.get("groupselector-inv"))
        res, msg = current_user.invite_user_to_group(to_group_id, user_id)
        return msg

@app.route('/api/delete_struct')
@login_required
def delete_struct():
    return ""

@app.post('/api/search_users')
def search_users():
    search_string = request.form.get('search')
    if len(search_string) == 0:
        users = []
    else:
        users = User.query.filter(User.username.ilike(f"%{search_string}%")).limit(5).all()
    return render_template('api/search_users.html', users=users)

@app.route('/api/create_group', methods=['GET', 'POST'])
def create_group():
    if request.method == "GET":
        form = CreateGroupForm()
        return render_template('api/create_group_form.html', form=form)
    if request.method == "POST":
        form = CreateGroupForm(request.form)
        if form.validate_on_submit():
            group_name = form.groupname.data
            group = Group(group_name=group_name, owner_id=current_user.user_id)
            db.session.add(group)
            db.session.commit()
            current_user.add_user_to_group(group)
            db.session.commit()
            
            response = make_response("<p> <em> 🎉 🤘 Group created 🎉 🤘</em> </p>")
            response.headers['HX-Trigger'] = "reloadg"
            
            return response
        else:
            return render_template('api/create_group_form.html', form=form)
        

@app.route('/gt/<string:invite_token>')
def accept_invite_link(invite_token):
    if current_user.is_authenticated:
        group_id = verify_group_invite_token(invite_token)
        if group_id is None:
            flash(f"Invalid invite token")
            return redirect(url_for('groups'))
        else:
            group = Group.query.get(group_id)
            if group in current_user.groups:
                msg = Markup(f"You are already in group <i>{group.group_name}</i>")
                flash(msg)
                return redirect(url_for('groups'))
            current_user.add_user_to_group(group)
            msg = Markup(f"Joined group <i>{group.group_name}</i>!")
            flash(msg)
            return redirect(url_for('groups'))
    else:
        flash(f"Please sign in or register to accept invite")
        session['group_invite_token'] = invite_token
        return redirect(url_for('login'))


@app.route('/api/test', methods=['POST'])
def api_test():
    txt = request.form.get('T1')
    return f"<p> {txt} </p>"