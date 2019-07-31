import time

from flask import (
    render_template,
    request,
    redirect,
    url_for,
    Blueprint,
)

from models.board import Board
from models.reply import Reply

from models.topic import Topic
from routes.helper import (
    csrf_required,
    login_required,
    new_csrf_token,
    topic_owner,
    current_user,
)


"""
用户在这里可以
    发布话题
    删除话题
    查看详情
"""


main = Blueprint('route_topic', __name__)


@main.route('/<int:id>')
@login_required
def detail(id):
    # id = int(request.args['id'])
    # http://localhost:3000/topic/1
    # m = Topic.one(id=id)
    token = new_csrf_token()
    m = Topic.get(id)
    u = current_user()

    return render_template("topic/detail.html", topic=m, user=u, token=token)


@main.route("/delete")
@csrf_required
@topic_owner
@login_required
def delete():
    u = current_user()
    id = int(request.args['id'])
    print('删除 topic 用户是', u, id)
    Topic.delete(id)
    rs = Reply.all(topic_id=id)
    for r in rs:
        Reply.delete(r.id)
    return redirect(url_for('homepage.index'))


@main.route("/new")
@login_required
def new():
    board_id = int(request.args.get('board_id', -1))
    bs = Board.all()
    token = new_csrf_token()
    return render_template("topic/new.html", bs=bs, token=token, bid=board_id)


@main.route("/add", methods=["POST"])
@csrf_required
@login_required
def add():
    form = request.form.to_dict()
    u = current_user()
    Topic.add(form, user_id=u.id)
    return redirect(url_for('homepage.index'))


@main.route("/edit")
@csrf_required
@topic_owner
@login_required
def edit():
    id = int(request.args['id'])
    token = request.args['token']
    m = Topic.get(id)
    u = current_user()
    bs = Board.all()
    return render_template("topic/topic_edit.html", topic=m, user=u, token=token, bs=bs)


@main.route("/edit_refresh", methods=["POST"])
@topic_owner
@login_required
def edit_refresh():
    form = request.form.to_dict()
    form['updated_time'] = int(time.time())
    u = current_user()
    topic_id = request.args['id']
    t: Topic = Topic.get(topic_id)
    t.edit(form)
    return redirect(url_for('.detail', id=t.id, u=u))

