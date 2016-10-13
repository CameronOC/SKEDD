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
        validators=[DataRequired(), Email(message=None), Length(min=1, max=50)])