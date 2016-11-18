# project/email.py

from flask.ext.mail import Message
from itsdangerous import URLSafeTimedSerializer

from project import app, mail

ts = URLSafeTimedSerializer(app.config["SECRET_KEY"])

def send_email(to, subject, template):
    msg = Message(
        subject,
        recipients=[to],
        html=template,
        sender=app.config['MAIL_DEFAULT_SENDER']
    )
    mail.send(msg)