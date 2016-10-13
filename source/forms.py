# project/user/forms.py


from flask_wtf import Form
from wtforms import StringField, PasswordField, SelectField, DateTimeField
from wtforms.validators import DataRequired, Email, Length, EqualTo

from source.models import User


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