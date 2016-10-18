# project/models.py


import datetime

from source import db, bcrypt
from sqlalchemy import UniqueConstraint


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
    confirmed = db.Column(db.Boolean, nullable=False, default=False)
    confirmed_on = db.Column(db.DateTime, nullable=True)

    # membership relationship with Organization
    memberships = db.relationship('Membership', backref='member', lazy='dynamic')

    def __init__(self, email, password, confirmed, first_name, last_name, paid=False, admin=False, confirmed_on=None):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = bcrypt.generate_password_hash(password)
        self.registered_on = datetime.datetime.now()
        self.admin = admin
        self.confirmed = confirmed
        self.confirmed_on = confirmed_on

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

    # relationship with user
    # assigned_user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    # relationship with Position
    assigned_position_id = db.Column(db.Integer, db.ForeignKey('positions.id'))


class Membership(db.Model):
    __tablename__ = 'organization_members'

    id = db.Column(db.Integer, primary_key=True)
    joined = db.Column(db.Boolean, default=False, nullable=False)
    is_owner = db.Column(db.Boolean, default=False, nullable=False)

    member_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'))

    # makes it so that a user can't be a member of an organization multiple times
    UniqueConstraint('member_id', 'organization_id')

    def __init__(self, member, organization, is_owner=False, joined=False):
        self.member_id = member.id
        self.organization_id = organization.id
        self.is_owner = is_owner
        self.joined = joined

    def __repr__(self):
        return '<Organization: {}, Member: {}, joined: {}>'.format(self.organization_id, self.member_id, self.joined)


class Organization(db.Model):
    __tablename__ = "organizations"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    # membership relationship with users
    memberships = db.relationship('Membership', backref='organization', lazy='dynamic')

    # positions connected to organization
    owned_positions = db.relationship('Position',
                                      backref='Organization', lazy='dynamic')

    def __init__(self, name, owner):
        self.name = name
        self.owner_id = owner.id

    def __repr__(self):
        return '<name: {}>'.format(self.name)


claimed = db.Table('claimed',
                   db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
                   db.Column('position_id', db.Integer, db.ForeignKey('positions.id'))
                   )


class Position(db.Model):
    __tablename__ = "positions"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50))
    # shifts connected to Position
    assigned_shifts = db.relationship('Shift',
                                      backref='Position', lazy='dynamic')
    # Organization associated with shift
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'))
    # Users many to many relationship with position
    assigned_users = db.relationship('User', secondary=claimed,
                                     backref=db.backref('Position', lazy='dynamic'))

    def __init__(self, title, organization_id):
        self.title = title
        self.organization_id = organization_id

    def __repr__(self):
        return '<title: {}>'.format(self.title)
