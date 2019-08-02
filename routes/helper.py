import functools
import uuid
from functools import wraps

from flask import (
    request,
    redirect,
    url_for,
)

from models.topic import Topic
from models.user import User
from utils import log
import json
import redis


cache = redis.StrictRedis()


def current_user():
    session_id = request.cookies.get('cache_session', -1)
    log('session_id', session_id)
    # user_id = json.loads(cache.get(session_id))
    user_id = cache.get(session_id)
    log('user_id', user_id)
    if user_id is None:
        u = User.guest()
        return u
    else:
        user_id = json.loads(cache.get(session_id))
        u = User.one(id=user_id)
        if u is None:
            return User.guest()
        else:
            return u


# def login_required(route_function):
#     @functools.wraps(route_function)
#     def f():
#         log('login_required')
#         u = current_user()
#         if u is None:
#             log('游客用户')
#             return redirect(url_for('index.index'))
#         else:
#             log('登录用户', route_function)
#             return route_function()
#
#     return f


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        log('login_required')
        u = current_user()
        if u.username == '游客':
            log('游客用户')
            return redirect(url_for('index.index'))
        else:
            log('登录用户', f)
            return f(*args, **kwargs)

    return wrapper


# def current_user():
#     # uid = session.get('user_id', '')
#     # u: User = User.one(id=uid)
#     # type annotation
#     # User u = User.one(id=uid)
#     # return u
#     session_id = request.cookies.get('session', -1)
#     user_id = json.loads(cache.get(session_id))
#     if int(user_id) == -1:
#         u = User.one(id=1)
#     else:
#         u = User.one(id=user_id)
#     return u


def csrf_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        token = request.args['token']
        u = current_user()
        log('token value', cache.exists(token), json.loads(cache.get(token)), u.id)
        if cache.exists(token) and json.loads(cache.get(token)) == u.id:
            cache.delete(token)
            return f(*args, **kwargs)
        else:
            return redirect(url_for('homepage.index'))

    return wrapper


def topic_owner(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        u = current_user()
        id = int(request.args['id'])
        topic_user = Topic.one(id=id).user_id
        if topic_user == u.id:
            return f(*args, **kwargs)
        else:
            return redirect(url_for('homepage.index'))

    return wrapper


def new_csrf_token(u=None):
    if u is None:
        u = current_user()
    k = str(uuid.uuid4())
    v = u.id
    cache.set(k, v)
    return k


def session_user(id):
    session_id = 'user' + str(uuid.uuid4())
    user_id = id
    cache.set(session_id, user_id)
    return session_id


