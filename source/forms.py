# project/user/forms.py


from flask_wtf import Form
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Email, Length, EqualTo

from source.models import User


class CreateForm(Form):
    name = StringField('name', validators=[DataRequired(), Length(min=1, max=50)])


class InviteForm(Form):
    email = StringField(
        'email',
        validators=[DataRequired(), Email(message=None), Length(min=1, max=50),])
    first_name = StringField(
        'first_name',
        validators=[DataRequired(), Length(min=1, max=20)])
    last_name = StringField(
        'last_name',
        validators=[DataRequired(), Length(min=1, max=20)])


class JoinForm(Form):
    password = PasswordField(
        'password',
        validators=[DataRequired(), Length(min=6, max=25)]
    )
    confirm = PasswordField(
        'Repeat password',
        validators=[
            DataRequired(),
            EqualTo('password', message='Passwords must match.')
        ]
    )