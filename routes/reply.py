from flask import (
    request,
    redirect,
    url_for,
    Blueprint,
    render_template)

from models.message import Messages
from models.topic import Topic
from models.user import User
from models.reply import Reply
from routes.helper import current_user, login_required, csrf_required

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


@main.route("/delete")
@csrf_required
@login_required
def delete():
    u = current_user()
    topic = Topic.one(id=int(request.args['topic_id']))
    reply = Reply.one(id=int(request.args['reply_id']))
    if u.id == int(topic.user_id) or u.id == int(reply.user_id):
        Reply.delete(reply.id)
        return render_template("topic/detail.html", topic=topic, user=u)
    else:
        return redirect(url_for('route_topic.detail', id=topic.id))