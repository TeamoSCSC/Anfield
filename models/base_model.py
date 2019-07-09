import time

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String

from utils import log

db = SQLAlchemy()


def current_time():
    return int(time.time())


class SQLMixin(object):
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    created_time = Column(Integer, default=current_time)
    updated_time = Column(Integer, default=current_time)

    @classmethod
    def new(cls, form):
        m = cls()
        for name, value in form.items():
            setattr(m, name, value)

        m.save()

        return m

    @classmethod
    def update(cls, id, **kwargs):
        # User.update(12, username='scsc', password='123')
        # u.username = 'scsc'
        # db.session.add(u)
        # db.session.commit()
        m = cls.query.filter_by(id=id).first()
        for name, value in kwargs.items():
            setattr(m, name, value)

        m.save()

    @classmethod
    def all(cls, **kwargs):
        ms = cls.query.filter_by(**kwargs).all()
        return ms

    @classmethod
    def one(cls, **kwargs):
        ms = cls.query.filter_by(**kwargs).first()
        return ms

    @classmethod
    def find(cls, **kwargs):
        ms = cls.query.filter_by(**kwargs).first()
        if ms is None:
            return False
        else:
            return True

    @classmethod
    def delete(cls, id):
        cls.query.filter_by(id=id).delete()
        db.session.commit()

    @classmethod
    def columns(cls):
        return cls.__mapper__.c.items()

    def __repr__(self):
        """
        __repr__ 是一个魔法方法
        简单来说, 它的作用是得到类的 字符串表达 形式
        比如 print(u) 实际上是 print(u.__repr__())
        不明白就看书或者 搜
        """
        name = self.__class__.__name__
        s = ''
        for attr, column in self.columns():
            if hasattr(self, attr):
                v = getattr(self, attr)
                s += '{}: ({})\n'.format(attr, v)
        return '< {}\n{} >\n'.format(name, s)

    def save(self):
        db.session.add(self)
        db.session.commit()


class SQLModelPro(object):
    # User.all()
    # User.one()
    # join
    # prefetch
    # query = User.select()
    # if a > 1:
    #   query.where(id=1)
    # else:
    #   query.join('session', 'id', 'user_id').where(id=1)

    def __init__(self, form):
        # 因为 id 是数据库给的，所以最开始初始化的时候必须是 None
        self.id = form.get('id', None)

    @classmethod
    def table_name(cls):
        return '`{}`'.format(cls.__name__)

    @classmethod
    def select(cls, connection):
        # SELECT * FROM user
        sql_select = 'SELECT * FROM {}'.format(cls.table_name())
        return Query(sql_select, connection, cls)

    def __repr__(self):
        """
        __repr__ 是一个魔法方法
        简单来说, 它的作用是得到类的 字符串表达 形式
        比如 print(u) 实际上是 print(u.__repr__())
        不明白就看书或者 搜
        """
        name = self.__class__.__name__
        properties = ['{}: ({})'.format(k, v) for k, v in self.__dict__.items()]
        s = '\n'.join(properties)
        return '< {}\n{} >\n'.format(name, s)


class Query(object):
    def __init__(self, raw, connection, model):
        self.query = raw
        self.values = tuple()
        self.connection = connection
        self.model = model

    def where(self, **kwargs):
        if len(kwargs) > 0:
            sql_where = ' AND '.join(
                ['`{}`=%s'.format(k) for k in kwargs.keys()]
            )
            sql_where = '\tWHERE\t{}'.format(sql_where)
            self.query = '{}{}'.format(self.query, sql_where)
        log('ORM where <{}>'.format(self.query))

        self.values = tuple(kwargs.values())

        return self

    def all(self):
        log('ORM all <{}> <{}>'.format(self.query, self.values))

        ms = []
        with self.connection.cursor() as cursor:
            log('ORM execute all <{}>'.format(cursor.mogrify(self.query, self.values)))
            cursor.execute(self.query, self.values)
            result = cursor.fetchall()
            for row in result:
                if self.join_exit():
                    m = row
                else:
                    m = self.model(row)
                ms.append(m)
            return ms

    def one(self):
        self.query = '{} LIMIT 1'.format(self.query)
        log('ORM one <{}> <{}>'.format(self.query, self.values))

        with self.connection.cursor() as cursor:
            log('ORM execute one <{}>'.format(cursor.mogrify(self.query, self.values)))
            cursor.execute(self.query, self.values)
            result = cursor.fetchone()
            if result is None:
                return None
            else:
                if self.join_exit():
                    return result
                else:
                    return self.model(result)

    def join(self, target_model, field, target_field):
        # JOIN topic on user.id=topic.user_id
        target_table = target_model.table_name()
        table = self.model.table_name()
        sql_join = 'JOIN {} on {}.{}={}.{}'.format(
            target_table, table, field, target_table, target_field
        )
        self.query = '{}\t{}'.format(self.query, sql_join)
        return self

    def join_exit(self):
        exist = 'JOIN' in self.query
        return exist

