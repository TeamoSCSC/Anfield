import time

from flask import (
    Flask,
    url_for,
    Response,
    abort,
)
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

# web framework
# web application
# __main__
import secret
from models.base_model import db
from models.board import Board
from models.reply import Reply
from models.topic import Topic
from models.user import User
from routes import index
from routes.helper import current_user
from utils import log

"""
在 flask 中，模块化路由的功能由 蓝图（Blueprints）提供
蓝图可以拥有自己的静态资源路径、模板路径（现在还没涉及）
用法如下
"""
# 注册蓝图
# 有一个 url_prefix 可以用来给蓝图中的每个路由加一个前缀
# import routes.index as index_view
from routes.index import main as index_routes
from routes.topic import main as topic_routes
from routes.reply import main as reply_routes
from routes.homepage import main as homepage_routes
from routes.personal import main as personal_routes
from routes.message import main as mail_routes
from routes.resetpassword import main as reset_routes
from routes.index import not_found


# @app.template_filter()
def count(input):
    log('count using jinja filter')
    return len(input)


class UserModelView(ModelView):
    def is_accessible(self):
        u = current_user()
        if u.id == 1:
            return url_for('admin.index')
        else:
            return abort(Response('没有权限'))
    # column_searchable_list = ('username', 'password')


def format_time(unix_timestamp):
    f = '%Y-%m-%d %H:%M:%S'
    value = time.localtime(unix_timestamp)
    formatted = time.strftime(f, value)
    return formatted


def configured_app():
    app = Flask(__name__)
    # 设置 secret_key 来使用 flask 自带的 session
    # 这个字符串随便设置什么内容都可以
    app.secret_key = secret.secret_key
    # 数据返回顺序
    # mysql -> pymysql -> sqlalchemy -> route
    # 初始化顺序
    # app -> flask-sqlalchemy -> sqlalchemy -> pymysql -> mysql

    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:{}@localhost/Anfield?charset=utf8mb4'.format(
        secret.database_password
    )
    db.init_app(app)

    app.register_blueprint(index_routes)
    app.register_blueprint(topic_routes, url_prefix='/topic')
    app.register_blueprint(reply_routes, url_prefix='/reply')
    app.register_blueprint(homepage_routes, url_prefix='/homepage')
    app.register_blueprint(personal_routes, url_prefix='/personal')
    app.register_blueprint(mail_routes, url_prefix='/mail')
    app.register_blueprint(reset_routes, url_prefix='/reset')
    log('url map', app.url_map)

    app.template_filter()(count)
    app.template_filter()(format_time)
    app.errorhandler(404)(not_found)

    admin = Admin(app, name='Anfield', template_mode='bootstrap3')
    admin.add_view(UserModelView(User, db.session))
    admin.add_view(UserModelView(Topic, db.session))
    admin.add_view(UserModelView(Reply, db.session))
    mv = UserModelView(Board, db.session)
    admin.add_view(mv)
    # Add administrative views here

    return app


# 运行代码
if __name__ == '__main__':
    # debug 模式可以自动加载你对代码的变动, 所以不用重启程序
    # host 参数指定为 '0.0.0.0' 可以让别的机器访问你的代码
    # 自动 reload jinja
    app = configured_app()
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.jinja_env.auto_reload = True
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    config = dict(
        debug=True,
        host='localhost',
        port=3000,
    )
    app.run(**config)
