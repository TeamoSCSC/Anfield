import uuid
from functools import wraps

from flask import session, abort, request
import json
from models.user import User
from routes.helper import cache


def current_user():
    session_id = request.cookies.get('session', -1)
    user_id = json.loads(cache.get(session_id))
    if int(user_id) == -1:
        u = User.one(id=1)
    else:
        u = User.one(id=user_id)
    return u


def get_user(id):
    u = User.one(id=id)
    return u