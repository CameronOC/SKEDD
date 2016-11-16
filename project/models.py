# project/models.py


import datetime

from project import db, bcrypt
from sqlalchemy import UniqueConstraint

position_assignments = db.Table('position_assignments',
                                db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
                                db.Column('position_id', db.Integer, db.ForeignKey('positions.id'))
                                )


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
    start_time = db.Column(db.String, nullable=False)
    end_time = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=True)

    # relationship with user
    assigned_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    # relationship with position
    position_id = db.Column(db.Integer, db.ForeignKey('positions.id'))

    def __init__(self, position_id, assigned_user_id, start_time, end_time, description):
        self.assigned_user_id = assigned_user_id
        self.position_id = position_id
        self.start_time = start_time
        self.end_time = end_time
        self.description = description
        
    def update  (   self,
                    position_id=0, 
                    assigned_user_id=0,
                    start_time=None,
                    end_time=None,
                    description=''
                ):
        """
        Updates fields of this shift in database
        :param shift:
        :param pos_key:
        :param assigned_user_id:
        :param start_time:
        :param end_time
        :return:
        """
        if position_id is not 0: 
            self.position_id = position_id
        if assigned_user_id is not 0:
            self.assigned_user_id = assigned_user_id
        if start_time is not None:
            self.start_time = start_time
        if end_time is not None:
            self.end_time = end_time
        if description is not '':
            self.description = description
    
        db.session.commit()


class Membership(db.Model):
    __tablename__ = 'organization_members'

    id = db.Column(db.Integer, primary_key=True)
    joined = db.Column(db.Boolean, default=False, nullable=False)
    is_owner = db.Column(db.Boolean, default=False, nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)

    member_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'))

    # makes it so that a user can't be a member of an organization multiple times
    UniqueConstraint('member_id', 'organization_id')

    def __init__(self, member_id, organization_id, is_owner=False, joined=False, is_admin=False):
        self.member_id = member_id
        self.organization_id = organization_id
        self.is_owner = is_owner
        self.joined = joined
        self.is_admin = is_admin

    def __repr__(self):
        return '<Organization: {}, Member: {}, joined: {}>'.format(self.organization_id, self.member_id, self.joined)
        
    def change_admin(self):
        self.is_admin = not self.is_admin
        db.session.commit()
        

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

    def __init__(self, name, owner_id):
        self.name = name
        self.owner_id = owner_id

    def __repr__(self):
        return '<name: {}>'.format(self.name)


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
    assigned_users = db.relationship(
        'User',
        secondary=position_assignments,
        backref=db.backref('Position', lazy='dynamic'))

    def __init__(self, title, organization_id):
        self.title = title
        self.organization_id = organization_id

    def __repr__(self):
        return '<title: {}>'.format(self.title)
