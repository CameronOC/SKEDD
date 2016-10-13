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


class Membership(db.Model):

    __tablename__ = 'organization_members'

    id = db.Column(db.Integer, primary_key=True)
    joined = db.Column(db.Boolean, default=False, nullable=False)

    member_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'))

    # makes it so that a user can't be a member of an organization multiple times
    UniqueConstraint('member_id', 'organization_id')

    def __init__(self, member, organization):
        self.member_id = member.id
        self.organization_id = organization.id

    def __repr__(self):
        return '<Organization: {}, Member: {}, joined: {}>'.format(self.organization_id, self.member_id, self.joined)


class Organization(db.Model):

    __tablename__ = "organizations"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    # membership relationship with users
    memberships = db.relationship('Membership', backref='organization', lazy='dynamic')


    def __init__(self, name, owner):
        self.name = name
        self.owner_id = owner.id

    def __repr__(self):
        return '<name: {}>'.format(self.name)

