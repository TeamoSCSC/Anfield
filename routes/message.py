from flask import (
    render_template,
    request,
    redirect,
    url_for,
    Blueprint,
)

from routes import *

from models.message import Messages
main = Blueprint('route_mail', __name__)


@main.route("/add", methods=["POST"])
def add():
    form = request.form.to_dict()
    u = current_user()
    receiver = User.one(username=form['receiver'])
    if receiver is not None:
        # 发邮件
        receiver_id = receiver.id
        title = '发件人{} 标题{}'.format(u.username, form['title'])
        Messages.send(
            title=title,
            content=form['content'],
            sender_id=u.id,
            receiver_id=receiver_id
        )
        return redirect(url_for('.index'))
    else:
        return redirect(url_for('.index'))


@main.route('/')
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
def view(id):
    message = Messages.one(id=id)
    u = current_user()
    # if u.id == mail.receiver_id or u.id == mail.sender_id:
    if u.id in [message.receiver_id, message.sender_id]:
        return render_template('mail/detail.html', message=message)
    else:
        return redirect(url_for('.index'))
