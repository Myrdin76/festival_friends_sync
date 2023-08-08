import datetime
from functools import wraps

from flask_login import current_user
from flask import abort

from app.models import Group


def membership_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        group_id = kwargs.get("group_id")
        print("group_id", group_id)
        group = Group.query.get(group_id)
        if group in current_user.groups:
            return f(*args, **kwargs)
        else:
            abort(403)

    return wrap