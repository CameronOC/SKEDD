# project/models.py


import datetime

from source import db, bcrypt


class User(db.Model):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    registered_on = db.Column(db.DateTime, nullable=False)
    admin = db.Column(db.Boolean, nullable=False, default=False)
        
    # relationship with shifts
    shifts = db.relationship("Shift", backref="user")

    def __init__(self, email, password, paid=False, admin=False):
        self.email = email
        self.password = bcrypt.generate_password_hash(password)
        self.registered_on = datetime.datetime.now()
        self.admin = admin

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    def __repr__(self):
        return '<email {}>'.format(self.email)
        
        
class Shift(db.Model):
	
	__tablename__ = "shifts"
	
	id = db.Column(db.Integer, primary_key=True)
	day = db.Column(db.String, nullable=False)
	start_time = db.Column(db.DateTime, nullable=False)
	end_time = db.Column(db.DateTime, nullable=False)
	duration = db.Column(db.String, nullable=False)
	
	# relationship with user
	assigned_user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
	
	def __init__(self, assigned_user_id, day):
		self.assigned_user_id = assigned_user_id
		self.day = day
		self.start_time = datetime.datetime.now()
		self.end_time = datetime.datetime.now()
		#self.start_time = start_time
		#self.end_time = end_time
		self.duration = datetime.time(0, 0, (self.end_time - self.start_time).seconds).strftime("%H:%M")

