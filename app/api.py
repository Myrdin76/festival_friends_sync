from flask import render_template, request, jsonify, redirect, url_for, make_response
from flask_login import login_required, current_user
import pandas as pd

from app import app, db
from app.models import User, Artist, Group
from app.forms import ChangeUsernameForm, EmptyForm
# from app.datastore import ArtistStore

@app.route('/api/fill_table')
def fill_table():
    stage = request.args.get('stageselector')
    day = request.args.get('dayselector')
    if stage == 'All' and day == 'All':
        data = Artist.query.all()
    elif stage == 'All':
        data = Artist.query.filter_by(day=day).all()
    elif day == 'All':
        data = Artist.query.filter_by(stage=stage).all()
    else:
        data = Artist.query.filter_by(stage=stage, day=day).all()
        
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

@app.route('/api/delete_struct')
@login_required
def delete_struct():
    return ""

@app.route('/api/test', methods=['POST'])
def api_test():
    txt = request.form.get('T1')
    return f"<p> {txt} </p>"