import uuid

from flask import (
    render_template,
    request,
    redirect,
    url_for,
    Blueprint,
)

from models.board import Board
from models.message import Messages
from models.user import User
from routes import current_user

from models.topic import Topic
from routes.helper import new_csrf_token

main = Blueprint('reset', __name__)


def reset_token():
    token = str(uuid.uuid4())
    return token


user_token = {}


@main.route("/send", methods=['POST'])
def reset_send_mail():
    username = request.form['username']
    u = User.one(username=username)
    token = reset_token()
    user_token[token] = u.id
    Messages.send(
        title='sc论坛重置密码',
        content='http://152.136.129.239/reset/view?token={}'.format(token),
        sender_id=0,
        receiver_id=u.id
    )
    return redirect(url_for('index.index'))


@main.route("/view", methods=['GET'])
def reset_view():
    print('???')
    token = str(request.args.get('token', None))
    u_id = user_token.get(token, -1)
    if token is not None and u_id != -1:
        u = User.one(id=u_id)
        return render_template('reset.html', user=u, token=token)
    else:
        return redirect(url_for('index.index'))


@main.route("/update/token=<string:token>", methods=['POST'])
def reset_update(token):
    print('321')
    u_id = user_token.get(token, -1)
    password = request.form['password']
    if u_id != -1 and len(password) > 2:
        u = User.one(id=u_id)
        u.password = u.salted_password(password)
        User.update(u_id, password=u.password)
        return redirect(url_for('index.index'))
    else:
        return redirect(url_for('index.index'))