from flask import (
    request,
    redirect,
    url_for,
    Blueprint,
)

from models.message import Messages
from models.user import User
from models.reply import Reply
from routes.helper import current_user

main = Blueprint('route_reply', __name__)


def users_from_content(content):
    # 内容 @123 内容
    # 如果用户名含有空格 就不行了 @name 123
    # 'a b c' -> ['a', 'b', 'c']
    parts = content.split()
    users = []

    for p in parts:
        if p.startswith('@'):
            username = p[1:]
            u = User.one(username=username)
            print('users_from_content <{}> <{}> <{}>'.format(username, p, parts))
            if u is not None:
                users.append(u)

    return users


def send_mails(sender, receivers, reply_link, reply_content):
    print('send_mail', sender, receivers, reply_content)
    content = '链接：{}\n内容：{}'.format(
        reply_link,
        reply_content
    )
    for r in receivers:
        title = '你被 {} AT 了'.format(sender.username)
        Messages.send(
            title=title,
            content=content,
            sender_id=sender.id,
            receiver_id=r.id
        )


@main.route("/add", methods=["POST"])
def add():
    form = request.form
    u = current_user()

    content = form['content']
    users = users_from_content(content)
    send_mails(u, users, request.referrer, content)

    form = request.form.to_dict()
    u = current_user()
    print('DEBUG', form)
    m = Reply.add(form, user_id=u.id)
    return redirect(url_for('route_topic.detail', id=m.topic_id))

