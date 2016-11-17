# project/email.py

from flask.ext.mail import Message
import os
import sendgrid


from project import app, mail


def send_email(to, subject, template):
    sg = sendgrid.SendGridClient('SENDGRID_API_KEY')
    message = sendgrid.Mail()

    message.add_to("cjplanes@gmail.com")
    message.set_from("skedd.mail@gmail.com")
    message.set_subject("Sending with SendGrid is Fun")
    message.set_html("and easy to do anywhere, even with Python")

    sg.send(message)
    #msg = Message(
     #   subject,
      #  recipients=[to],
       # html=template,
        #sender=app.config['MAIL_DEFAULT_SENDER']
    #)
    #mail.send(msg)