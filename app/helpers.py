import jwt
from datetime import datetime, timedelta
from time import time
from urllib.parse import urljoin

from flask import request

from app import config
from app.wrappers import membership_required


def get_group_invite_token(group_id: int, expires_in: int = 3600 * 72):
    return jwt.encode({"group_id": str(group_id), "exp": time() + expires_in}, config.SECRET_KEY, algorithm="HS256")


def create_group_invite_link(group_id: int):
    base_url = config.BASE_URL + "/gt/"
    token = get_group_invite_token(group_id)
    print("token", token)
    url = urljoin(base_url, token)
    
    return url

def verify_group_invite_token(token: str):
    try:
        data = jwt.decode(token, config.SECRET_KEY, algorithms=["HS256"])
        print("data", data)
        return data["group_id"]
    except:
        return None