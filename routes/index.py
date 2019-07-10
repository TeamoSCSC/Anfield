import os
import uuid
import json
import flask
from flask import (
    render_template,
    request,
    redirect,
    session,
    url_for,
    Blueprint,
    abort,
    send_from_directory, current_app)
from werkzeug.datastructures import FileStorage

from models.user import User
from routes.helper import session_user, cache, current_user

from utils import log

main = Blueprint('index', __name__)


# def current_user():
#     session_id = request.cookies.get('session', -1)
#     user_id = json.loads(cache.get(session_id))
#     if int(user_id) == -1:
#         u = User.one(id=1)
#     else:
#         u = User.one(id=user_id)
#     return u


"""
用户在这里可以
    访问首页
    注册
    登录

用户登录后, 会写入 session, 并且定向到 /profile
"""


@main.route("/")
def index():
    # u = current_user()
    # return render_template("index.html", user=u)
    return render_template("login.html")


@main.route("/rg")
def rg():
    # u = current_user()
    # return render_template("index.html", user=u)
    return render_template("register.html")


@main.route("/register", methods=['POST'])
def register():
    # form = request.args
    form = request.form
    # 用类函数来判断
    u = User.register(form)
    return redirect(url_for('.index'))


@main.route("/login", methods=['POST'])
def login():
    form = request.form
    u = User.validate_login(form)
    print('login user <{}>'.format(u))
    if u is None:
        # 转到 topic.index 页面
        return redirect(url_for('.index'))
    else:
        # session 中写入 user_id
        # session['user_id'] = u.id
        # 设置 cookie 有效期为 永久
        # session.permanent = True
        session_id = session_user(u.id)
        res = current_app.make_response(flask.redirect(url_for('homepage.index')))
        res.set_cookie('cache_session', session_id)
        # return redirect(url_for('homepage.index'))
        return res


@main.route('/image/add', methods=['POST'])
def avatar_add():
    file: FileStorage = request.files['avatar']
    suffix = file.filename.split('.')[-1]
    filename = '{}.{}'.format(str(uuid.uuid4()), suffix)
    path = os.path.join('images', filename)
    file.save(path)

    u = current_user()
    User.update(u.id, image='/images/{}'.format(filename))

    return redirect(url_for('personal.edit', id=u.id))


@main.route('/images/<filename>')
def image(filename):
    return send_from_directory('images', filename)


def not_found(e):
    return render_template('404.html')
