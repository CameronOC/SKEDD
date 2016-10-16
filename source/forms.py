# project/user/forms.py


from flask_wtf import Form
from wtforms import StringField, PasswordField, SelectField, DateTimeField
from wtforms.validators import DataRequired, Email, Length, EqualTo


class CreateForm(Form):
    name = StringField('name', validators=[DataRequired(), Length(min=1, max=50)])
    
class ShiftDay(Form):
    position = StringField('position', validators=[DataRequired(), Length(min=1, max=20)])
    day = SelectField('day', choices=[	('Monday', 'Monday'),
            ('Tuesday', 'Tuesday'),
            ('Wednesday', 'Wednesday'),
            ('Thursday', 'Thursday'),
            ('Friday', 'Friday'),
            ('Saturday', 'Saturday'),
            ('Sunday', 'Sunday')])
    start_time = DateTimeField('StartTime', format='%H:%M')
    end_time = DateTimeField('EndTime', format='%H:%M')
    am_or_pm = SelectField('AMorPM', choices=[('AM', 'AM'), ('PM', 'PM')])


class InviteForm(Form):
    email = StringField(
        'email',
        validators=[DataRequired(), Email(message=None), Length(min=1, max=50), ])
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


class PositionForm(Form):
    name = StringField('title', validators=[DataRequired(), Length(min=1, max=50)])
