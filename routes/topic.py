from flask import (
    render_template,
    request,
    redirect,
    url_for,
    Blueprint,
)

from models.board import Board
from routes import current_user

from models.topic import Topic
from routes.helper import csrf_required, login_required, new_csrf_token

main = Blueprint('topic', __name__)


@main.route("/")
def index():
    ms = Topic.all()
    u = current_user()
    return render_template("topic/index.html", ms=ms, user=u)


@main.route('/<int:id>')
def detail(id):
    # id = int(request.args['id'])
    # http://localhost:3000/topic/1
    # m = Topic.one(id=id)
    m = Topic.get(id)
    u = current_user()

    return render_template("topic/detail.html", topic=m, user=u)


@main.route("/delete")
@csrf_required
@login_required
def delete():
    u = current_user()
    id = int(request.args['id'])
    print('删除 topic 用户是', u, id)
    Topic.delete(id)
    return redirect(url_for('homepage.index'))


@main.route("/new")
def new():
    board_id = int(request.args.get('board_id', -1))
    bs = Board.all()
    token = new_csrf_token()
    return render_template("topic/new.html", bs=bs, token=token, bid=board_id)


@main.route("/add", methods=["POST"])
@csrf_required
def add():
    form = request.form.to_dict()
    u = current_user()
    Topic.add(form, user_id=u.id)
    return redirect(url_for('homepage.index'))

