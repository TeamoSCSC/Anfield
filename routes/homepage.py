from flask import (
    render_template,
    request,
    redirect,
    url_for,
    Blueprint,
)

from models.board import Board


from models.topic import Topic
from routes.helper import new_csrf_token, current_user

main = Blueprint('homepage', __name__)


@main.route("/")
def index():
    u = current_user()
    board_id = int(request.args.get('board_id', -1))
    if board_id == -1:
        ms = Topic.all()
    else:
        ms = Topic.all(board_id=board_id)
    token = new_csrf_token()
    bs = Board.all()
    return render_template("homepage.html", ms=ms, token=token, bs=bs, bid=board_id, user=u)


@main.route("/search")
def search():
    u = current_user()
    board_id = int(request.args.get('board_id', -1))
    content = str(request.args.get('content', -1))
    ts = Topic.all()
    ms = []
    for topic in ts:
        if content in topic.content:
            ms.append(topic)
    token = new_csrf_token()
    bs = Board.all()
    return render_template("homepage.html", ms=ms, token=token, bs=bs, bid=board_id, user=u)