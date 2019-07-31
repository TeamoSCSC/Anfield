from sqlalchemy import (
    Integer,
    Column,
    UnicodeText,
    Unicode,
)
from models.base_model import (
    SQLMixin,
    db,
)
from models.user import User
from models.reply import Reply


class Topic(SQLMixin, db.Model):
    views = Column(Integer, nullable=False, default=0)
    title = Column(Unicode(50), nullable=False)
    content = Column(UnicodeText, nullable=False)
    user_id = Column(Integer, nullable=False)
    board_id = Column(Integer, nullable=False)

    @classmethod
    def add(cls, form, user_id):
        form['user_id'] = user_id
        m = super().new(form)
        return m

    def edit(self, form):
        self.content = form['content']
        self.board_id = form['board_id']
        self.updated_time = form['updated_time']
        self.save()

    @classmethod
    def get(cls, id):
        m = cls.one(id=id)
        m.views += 1
        m.save()
        return m

    def user(self):
        u = User.one(id=self.user_id)
        return u

    def replies(self):
        ms = Reply.all(topic_id=self.id)
        return ms

    def reply_count(self):
        count = len(self.replies())
        return count
