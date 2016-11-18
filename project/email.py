# project/email.py
import sendgrid
import os
from sendgrid.helpers.mail import *
from flask.ext.mail import Message
import os
import sendgrid
from sendgrid.helpers.mail import *
from project import app, mail


def send_email(to, subject, template):
    sg = sendgrid.SendGridAPIClient(apikey=os.environ.get('SENDGRID_API_KEY'))
    from_email = Email("skedd.mail@gmail.com")
    to_email = Email(to)
    content = Content("text/plain", "and easy to do anywhere, even with Python")
    mail = Mail(from_email, subject, to_email, content)
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