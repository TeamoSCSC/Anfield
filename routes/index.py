import os
import uuid
from random import randint

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

from celery_tasks import send_mail
from config import admin_mail
from models.user import User
from routes.helper import (
    session_user,
    current_user,
    login_required, cache)


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
    return render_template("rg.html")


@main.route("/register/mail", methods=['POST'])
def register_mail():
    form = request.form
    email = form['email']
    u = User.one(email=email)
    if u is None:
        verify_code = ''.join([str(randint(0, 9)) for i in range(6)])
        cache.set(email, verify_code, 600)
        title = '欢迎注册Teamodou BBS'
        content = '欢迎注册Teamodou BBS。您的验证码为{}，请在一分钟之内完成注册' \
                  '如果不是您本人的操作，请无视本邮件。'.format(verify_code)
        try:
            send_mail(
                subject=title,
                author=admin_mail,
                to=email,
                content=content, )
            flash('验证码已发送至您的邮箱，请查收!')
            return redirect(url_for('index.register_view', email=email))

        except ValueError:
            flash('邮箱格式错误！')
            return redirect(url_for('index.rg'))
    else:
        flash('该邮箱已被注册！')
        return redirect(url_for('index.rg'))


@main.route("/register/view", methods=['GET'])
def register_view():
    email = request.args['email']
    return render_template("register.html", email=email)


@main.route("/register", methods=['POST'])
def register():
    form = request.form.to_dict()
    email = form['email']
    verify_code = form.pop('verify_code', '')
    if cache.exists(email) and int(cache.get(email)) == int(verify_code):
        u = User.register(form)
        if u is not None:
            session_id = session_user(u.id)
            res = current_app.make_response(flask.redirect(url_for('homepage.index')))
            res.set_cookie('cache_session', session_id)
            return res
        else:
            flash('用户名长度必须大于2或用户名已存在！')
            return redirect(url_for('index.register_view', email=email))
    else:
        flash('验证码错误')
        return redirect(url_for('index.register_view', email=email))


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
