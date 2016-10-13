# project/models.py


import datetime

from source import db, bcrypt


class User(db.Model):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, unique=True, nullable=False)
    first_name = db.Column(db.String(20))
    last_name = db.Column(db.String(20))
    password = db.Column(db.String, nullable=False)
    registered_on = db.Column(db.DateTime, nullable=False)
    admin = db.Column(db.Boolean, nullable=False, default=False)
        
    # relationship with shifts
    shifts = db.relationship("Shift", backref="user")

	# relationship with organization
    orgs_owned = db.relationship('Organization', backref='owner', lazy='dynamic')

    def __init__(self, email, password, first_name, last_name, paid=False, admin=False):
        self.first_name = first_name
        self.last_name = last_name
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
	duration = db.Column(db.DateTime, nullable=False)
	
	# relationship with user
	assigned_user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
	
	# relationship with position
	#position_id = db.Column(db.Integer, db.ForeignKey('positions.id'))
	
	def __init__(self, assigned_user_id, day, start_time, end_time):
		self.assigned_user_id = assigned_user_id
		#self.position_id = position_id
		self.day = day
		#self.start_time = datetime.datetime.now()
		#self.end_time = datetime.datetime.now()
		self.start_time = start_time
		self.end_time = end_time
		
		zero = datetime.datetime.strptime('00:00', '%H:%M')	# zero o'clock datetime to add timedelta object to (end_time - start_time)
		self.duration = zero + (self.end_time - self.start_time)


class Organization(db.Model):

    __tablename__ = "organizations"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __init__(self, name, owner):
        self.name = name
        self.owner_id = owner.id

    def __repr__(self):
        return '<name: {}>'.format(self.name)
