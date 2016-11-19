# project/email.py
import sendgrid
import os
from sendgrid.helpers.mail import *
from flask.ext.mail import Message
from itsdangerous import URLSafeTimedSerializer

from project import app, mail

ts = URLSafeTimedSerializer(app.config["SECRET_KEY"])

def send_email(to, subject, template):
    sg = sendgrid.SendGridAPIClient(apikey=os.environ.get('SENDGRID_API_KEY'))
    from_email = Email("skedd.mail@gmail.com")
    to_email = Email(to)
    content = Content("text/html", template)
    mail = Mail(from_email, subject, to_email, content)
    response = sg.client.mail.send.post(request_body=mail.get())
    #msg = Message(
     #   subject,
      #  recipients=[to],
       # html=template,
        #sender=app.config['MAIL_DEFAULT_SENDER']
    #)
    #mail.send(msg)
