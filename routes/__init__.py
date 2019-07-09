import uuid
from functools import wraps

from flask import session, abort, request
import json
from models.user import User
from routes.helper import cache
from utils import log


def current_user():
    session_id = request.cookies.get('cache_session', -1)
    log('session_id', session_id)
    user_id = json.loads(cache.get(session_id))
    log('user_id', user_id)
    if int(user_id) == -1:
        u = User.guest()
        return u
    else:
        u = User.one(id=user_id)
        if u is None:
            return User.guest()
        else:
            return u


def get_user(id):
    u = User.one(id=id)
    return u