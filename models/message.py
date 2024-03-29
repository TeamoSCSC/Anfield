from time import sleep

from flask import (
    url_for,
    redirect,
)
from marrow.mailer import Mailer
from sqlalchemy import (
    Column,
    Unicode,
    UnicodeText,
    Integer,
)

from celery_tasks import send_mail
from config import admin_mail
from models.base_model import (
    SQLMixin,
    db,
)
from models.user import User


# def configured_mailer():
#     config = {
#         'transport.debug': True,
#         'transport.timeout': 1,
#         'transport.use': 'smtp',
#         'transport.host': 'smtp.exmail.qq.com',
#         'transport.port': 465,
#         'transport.tls': 'ssl',
#         'transport.username': admin_mail,
#         'transport.password': secret.mail_password,
#     }
#     m = Mailer(config)
#     m.start()
#     return m
#
#
# mailer = configured_mailer()


# def send_mail(subject, author, to, content):
#     m = mailer.new(
#         subject=subject,
#         author=author,
#         to=to,
#     )
#     m.plain = content
#     mailer.send(m)


class Messages(SQLMixin, db.Model):
    title = Column(Unicode(50), nullable=False)
    content = Column(UnicodeText, nullable=False)
    sender_id = Column(Integer, nullable=False)
    receiver_id = Column(Integer, nullable=False)

    @staticmethod
    def send(title: str, content: str, sender_id: int, receiver_id: int):
        form = dict(
            title=title,
            content=content,
            sender_id=sender_id,
            receiver_id=receiver_id
        )
        Messages.new(form)

        receiver: User = User.one(id=receiver_id)
        send_mail(
            subject=title,
            author=admin_mail,
            to=receiver.email,
            content='站内信通知：\n {}'.format(content),
        )
        return redirect(url_for('route_mail.index'))

    @staticmethod
    def send_in(title: str, content: str, sender_id: int, receiver_id: int):
        form = dict(
            title=title,
            content=content,
            sender_id=sender_id,
            receiver_id=receiver_id
        )
        Messages.new(form)
        return redirect(url_for('route_mail.index'))

    def get_sender(self):
        u = User.one(id=self.sender_id)
        return u

    def get_receiver(self):
        u = User.one(id=self.receiver_id)
        return u
