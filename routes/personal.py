import uuid
from werkzeug.datastructures import FileStorage
from flask import (
    render_template,
    request,
    redirect,
    url_for,
    Blueprint,
    send_from_directory,
)
import os

from models.reply import Reply
from models.user import User
from models.topic import Topic
from routes.helper import (
    current_user,
    login_required,
)
from routes.myredis import cache

"""
用户在这里可以
    查看个人信息
    修改个人信息
"""


main = Blueprint('personal', __name__)


@main.route("/<int:id>")
@login_required
def index(id):
    m = Topic.all(user_id=id)
    r = Reply.all(user_id=id)
    r.sort(key=lambda r: r.created_time, reverse=True)
    m.sort(key=lambda m: m.created_time, reverse=True)
    rm = []
    for i in r:
        n = Topic.one(id=i.topic_id)
        setattr(n, 'reply_time', i.created_time)
        # n.reply_time = i.created_time
        rm.append(n)
    u = User.one(id=id)
    return render_template("personal.html", ms=m, rs=rm, user=u)


@main.route("/edit")
@login_required
def edit():
    u = current_user()
    return render_template("edit.html", user=u)


@main.route("/edit/password", methods=["POST"])
@login_required
def edit_password():
    u = current_user()
    key = 'user_id_{}'.format(u.id)
    form = request.form.to_dict()
    print('password', User.salted_password(form['old_pass']), u.password)
    if User.salted_password(form['old_pass']) == u.password and len(form['new_pass']) > 2:
        User.update(u.id, password=User.salted_password(form['new_pass']))
        cache.delete(key)
    return render_template("edit.html", user=u)


@main.route("/edit/usernameorsignatueoremail", methods=["POST"])
@login_required
def edit_usernameorsignatueoremail():
    u = current_user()
    key = 'user_id_{}'.format(u.id)
    form = request.form.to_dict()
    username = form.get('username', None)
    signature = form.get('signature', u.signature)
    email = form.get('email', u.email)
    if username is not None and not User.find(username=username):
        User.update(u.id, username=username, signature=signature, email=email)
    else:
        User.update(u.id, signature=signature, email=email)
    cache.delete(key)

    return render_template("edit.html", user=u)


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
    key = 'user_id_{}'.format(u.id)
    cache.delete(key)

    return redirect(url_for('personal.edit', id=u.id))


@main.route('/images/<filename>')
@login_required
def image(filename):
    return send_from_directory('images', filename)

