from flask import (
    render_template,
    request,
    redirect,
    url_for,
    Blueprint,
)

from models.user import User
from models.message import Messages
from routes.helper import current_user, login_required

"""
用户在这里可以
    查看来往私信
    发送私信
用户登录后, 会写入 session, 并且定向到 /profile
"""


main = Blueprint('route_mail', __name__)


@main.route("/add", methods=["POST"])
@login_required
def add():
    form = request.form.to_dict()
    u = current_user()
    receiver = User.one(username=form['receiver'])
    if receiver is not None:
        # 发邮件
        receiver_id = receiver.id
        title = '{}'.format(form['title'])
        Messages.send(
            title=title,
            content=form['content'],
            sender_id=u.id,
            receiver_id=receiver_id
        )
        return redirect(url_for('.index'))
    else:
        return redirect(url_for('.index'))


@main.route("/addin", methods=["POST"])
@login_required
def addin():
    form = request.form.to_dict()
    u = current_user()
    receiver = User.one(username=form['receiver'])
    if receiver is not None:
        # 发邮件
        receiver_id = receiver.id
        title = '{}'.format(form['title'])
        Messages.send_in(
            title=title,
            content=form['content'],
            sender_id=u.id,
            receiver_id=receiver_id
        )
        return redirect(url_for('.index'))
    else:
        return redirect(url_for('.index'))


@main.route('/')
@login_required
def index():
    u = current_user()

    send = Messages.all(sender_id=u.id)
    received = Messages.all(receiver_id=u.id)

    t = render_template(
        'mail/index.html',
        send=send,
        received=received,
        user=u,
    )
    return t


@main.route('/view/<int:id>')
@login_required
def view(id):
    message = Messages.one(id=id)
    u = current_user()
    # if u.id == mail.receiver_id or u.id == mail.sender_id:
    if u.id in [message.receiver_id, message.sender_id]:
        return render_template('mail/detail.html', message=message)
    else:
        return redirect(url_for('.index'))
