from flask import render_template, request, jsonify, redirect, url_for
from flask_login import login_required, current_user
import pandas as pd

from app import app
from app.models import User, Artist, Group
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
        
    return render_template('api_fill_table.html', data=data)

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
    print(gid)
    group = Group.query.get(gid)
    
    current_user.add_user_to_group(group)
    
    membergroups = current_user.groups
    
    return render_template('api_list_of_groups.html', membergroups=membergroups)


@app.route('/api/leave_group', methods=['GET', 'POST'])
def leave_group():
    gid = request.args.get('groupselector')
    print(gid)
    group = Group.query.get(gid)
    
    current_user.remove_user_from_group(group)
    
    membergroups = current_user.groups
    
    return render_template('api_list_of_groups.html', membergroups=membergroups)


@app.route('/api/get_friends')
def get_friends():
    gid = request.args.get('groupselector')
    group = Group.query.get(gid)
    
    return render_template('api_list_of_friends.html', group=group)


@app.route('/api/fill_personal')
def fill_personal():
    group_id = request.args.get('groupselector')
    
    # Get the users who are part of the specified group
    users_in_group = User.query.filter(User.groups.any(group_id=group_id)).all()
    users_in_group = [user for user in users_in_group if user.username != current_user.username]

    # Loop through all artists
    res = current_user.get_all_artists_ordered()
    for i in range(0,len(res)):
        # Get the users who are part of the specified group and are going to this artist
        users_going_to_artist = [
            user for user in users_in_group if res[i] in user.artists
        ]
        setattr(res[i], "friendsgoing", [user.username for user in users_going_to_artist])
    
    return render_template('api_fill_personal.html', data=res)


@app.route('/api/test', methods=['POST'])
def api_test():
    txt = request.form.get('T1')
    return f"<p> {txt} </p>"