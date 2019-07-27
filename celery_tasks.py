from celery import Celery
from marrow.mailer import Mailer
from config import admin_mail
import secret


celery = Celery('celery_tasks', backend='redis://localhost', broker='redis://localhost')


def configured_mailer():
    config = {
        'transport.debug': True,
        'transport.timeout': 1,
        'transport.use': 'smtp',
        'transport.host': 'smtp.exmail.qq.com',
        'transport.port': 465,
        'transport.tls': 'ssl',
        'transport.username': admin_mail,
        'transport.password': secret.mail_password,
    }
    m = Mailer(config)
    m.start()
    return m


mailer = configured_mailer()


# def send_mail(subject, author, to, content):
#     m = mailer.new(
#         subject=subject,
#         author=author,
#         to=to,
#     )
#     m.plain = content
#     mailer.send(m)


@celery.task(bind=True)
def send_mail(self, subject, author, to, content):
    try:
        m = mailer.new(
            subject=subject,
            author=author,
            to=to,
        )
        m.plain = content
        mailer.send(m)
    except Exception as exc:
        raise self.retry(exc=exc, countdown=3, max_retries=5)