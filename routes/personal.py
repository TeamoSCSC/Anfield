from flask import (
    render_template,
    request,
    redirect,
    url_for,
    Blueprint,
)

from models.reply import Reply
from models.user import User
from routes import current_user, get_user

from models.topic import Topic

main = Blueprint('personal', __name__)


@main.route("/<int:id>")
def index(id):
    u = current_user()
    if u.id == id:
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
    else:
        return redirect(url_for('homepage.index'))


@main.route("/<int:id>/edit")
def edit(id):
    u = current_user()
    if u.id == id:
        return render_template("edit.html", user=u)
    else:
        return redirect(url_for('homepage.index'))


@main.route("/<int:id>/edit/password", methods=["POST"])
def edit_password(id):
    u = User.one(id=id)
    form = request.form.to_dict()
    print('password', User.salted_password(form['old_pass']), u.password)
    if User.salted_password(form['old_pass']) == u.password and len(form['new_pass']) > 2:
        User.update(id, password=User.salted_password(form['new_pass']))
    return render_template("edit.html", user=u)


@main.route("/<int:id>/edit/usernameorsignatueoremail", methods=["POST"])
def edit_usernameorsignatueoremail(id):
    u = User.one(id=id)
    form = request.form.to_dict()
    username = form.get('username', None)
    signature = form.get('signature', u.signature)
    email = form.get('email', u.email)
    if username is not None and not User.find(username=username):
        User.update(id, username=username, signature=signature, email=email)
    else:
        User.update(id, signature=signature, email=email)
    return render_template("edit.html", user=u)

