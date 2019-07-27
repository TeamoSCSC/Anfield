from flask import (
    render_template,
    request,
    redirect,
    url_for,
    Blueprint,
)

from models.reply import Reply
from models.user import User
from models.topic import Topic
from routes.helper import current_user


"""
用户在这里可以
    查看个人信息
    修改个人信息
"""


main = Blueprint('personal', __name__)


@main.route("/<int:id>")
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
def edit():
    u = current_user()
    return render_template("edit.html", user=u)


@main.route("/edit/password", methods=["POST"])
def edit_password():
    u = current_user()
    form = request.form.to_dict()
    print('password', User.salted_password(form['old_pass']), u.password)
    if User.salted_password(form['old_pass']) == u.password and len(form['new_pass']) > 2:
        User.update(u.id, password=User.salted_password(form['new_pass']))
    return render_template("edit.html", user=u)


@main.route("/edit/usernameorsignatueoremail", methods=["POST"])
def edit_usernameorsignatueoremail():
    u = current_user()
    form = request.form.to_dict()
    username = form.get('username', None)
    signature = form.get('signature', u.signature)
    email = form.get('email', u.email)
    if username is not None and not User.find(username=username):
        User.update(u.id, username=username, signature=signature, email=email)
    else:
        User.update(u.id, signature=signature, email=email)
    return render_template("edit.html", user=u)

