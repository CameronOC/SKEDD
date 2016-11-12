# project/user/forms.py


from flask_wtf import Form
from wtforms import StringField, PasswordField, SelectField, BooleanField, HiddenField, SelectMultipleField
from wtforms.validators import DataRequired, Email, Length, EqualTo

from wtforms.ext.sqlalchemy.fields import QuerySelectField
from models import User, Position



class CreateForm(Form):
    name = StringField('name', validators=[DataRequired(), Length(min=1, max=50)])
    
class ShiftForm(Form):
    position_id = SelectField('positions', choices=[])
    
    assigned_user_id = SelectField('users', choices=[])
    
    description = StringField('description', validators=[Length(min=1, max=100)])
    
    repeating = BooleanField('repeating', default=False)

    repeat_list = SelectMultipleField('day', choices=[  (0, 'Monday'), 
                                                        (1, 'Tuesday'), 
                                                        (2, 'Wednesday'), 
                                                        (3, 'Thursday'), 
                                                        (4, 'Friday'), 
                                                        (5, 'Saturday'), 
                                                        (6, 'Sunday')])
                                        
    start_time = HiddenField('StartTime')
    end_time = HiddenField('EndTime')

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

#this form probably needs to be editted but its not throwing a error so ill keep it like it is for now
class ClaimPositionForm(Form):
    user_id = User.id
    position_id = Position.id

class PositionForm(Form):
    name = StringField('title', validators=[DataRequired(), Length(min=1, max=50)])
