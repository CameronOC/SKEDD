# project/email.py

from flask.ext.mail import Message
import os
import sendgrid
from sendgrid.helpers.mail import *

from project import app, mail


def send_email(to, subject, template):
    sg = sendgrid.SendGridAPIClient(apikey=os.environ.get('SENDGRID_API_KEY'))
    from_email = Email(os.environ['APP_MAIL_USERNAME'])
    content = Content("text/plain", "Hello, Email!")
    mail = Mail(from_email, subject, to, content)
    response = sg.client.mail.send.post(request_body=mail.get())
    print(response.status_code)
    print(response.body)
    print(response.headers)
    #msg = Message(
     #   subject,
      #  recipients=[to],
       # html=template,
        #sender=app.config['MAIL_DEFAULT_SENDER']
    #)
    #mail.send(msg)