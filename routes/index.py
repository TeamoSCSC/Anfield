import os
import uuid
import flask
from flask import (
    render_template,
    request,
    redirect,
    url_for,
    Blueprint,
    send_from_directory,
    current_app,
    flash,
)

from werkzeug.datastructures import FileStorage
from models.user import User
from routes.helper import (
    session_user,
    current_user,
    login_required)


"""
用户在这里可以
    注册
    登录
用户登录后, 会写入 session, 并且定向到 /profile
"""


main = Blueprint('index', __name__)


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
        flash('用户名或密码错误')
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


@main.route("/logout", methods=['GET'])
def logout():
    res = current_app.make_response(redirect(url_for('index.index')))
    res.delete_cookie('cache_session')
    return res


@main.route('/image/add', methods=['POST'])
@login_required
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
@login_required
def image(filename):
    return send_from_directory('images', filename)


def not_found(e):
    return render_template('404.html')
