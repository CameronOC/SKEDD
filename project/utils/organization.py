import datetime
from project import db, bcrypt
from project.models import Organization, User, Membership, Position, Shift
from project.email import send_email
from project.utils.token import confirm_token, generate_invitation_token

from flask import render_template, flash, url_for, g
from flask_login import login_user

def create_organization(name, owner_id):
    """
    Creates a new organization with paramaters and returns the created
    organization object
    :param owner_id:
    :param name:
    :return:
    """
    org = Organization(name=name, owner_id=owner_id)
    db.session.add(org)
    db.session.commit()

    membership = Membership(
        member_id=owner_id,
        organization_id=org.id,
        is_owner=True,
        joined=True
    )
    db.session.add(membership)
    db.session.commit()

    return org, membership


def get_user(id):
    """
    Gets a user by ID
    :param id:
    :return:
    """
    return User.query.get(id)


def get_organization(id):
    """
    gets an organization by id and returns the object or None
    if it doesn't exist
    :param id:
    :return:
    """
    return Organization.query.get(id)

def get_position(id):
    """
    Gets a position object based on id
    :param id:
    :return:
    """
    return Position.query.get(id)
    
def get_shift(id):
    """
    Gets a shift object based on id
    :param id:
    :return:
    """
    return Shift.query.get(id)

def get_membership(org, user):
    """
    Checks if a user is in an organization
    :param organization_id:
    :param user_id:
    :return:
    """
    return Membership.query.filter_by(member_id=user.id, organization_id=org.id).first()

def confirm_user(user, password=None):
    if password is not None:
        user.password = bcrypt.generate_password_hash(password)
    user.confirmed = True
    user.confirmed_on = datetime.datetime.now()
    db.session.commit()


def membership_from_key_token(key, token):
    """
    Gets a membership with a key and a token, or returns none
    :param key:
    :param token:
    :return:
    """
    email = confirm_token(token)
    user = User.query.filter_by(email=email).first()

    if user is None:
        return None

    org = get_organization(key)

    if org is None:
        return None

    membership = user.memberships.filter_by(organization_id=org.id).first()
    return membership


def invite_member(org, email, first_name, last_name):
    """
    Invite a user to the organization id, creating a dummy account if needed
    :param organization_id:
    :return:
    """
    user = User.query.filter_by(email=email).first()

    if user is None:
        user = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password="temp",
            confirmed=False
        )
        db.session.add(user)

    db.session.commit()

    membership = get_membership(org, user)

    if membership is not None:
        flash('This person is already a member of ' + org.name, 'danger')
    else:
        membership = Membership(
            member_id=user.id,
            organization_id=org.id
        )
        db.session.add(membership)
        db.session.commit()

        token = generate_invitation_token(user.email)

        confirm_url = url_for('main.confirm_invite', key=org.id, token=token, _external=True)

        html = render_template('emails/invitation.html', confirm_url=confirm_url, user=user, organization=org)

        subject = "You've been invited to use SKEDD"

        send_email(user.email, subject, html)

        flash('You succesfully invited ' + user.first_name + ' ' + user.last_name + '.', 'success')

    return membership


def confirm_invite(membership):
    """
    Confirms an invitation to an organization, if valid
    :param key:
    :param token:
    :return:
    """
    membership.joined = True
    db.session.commit()
    if g.user is None or g.user.id != membership.member.id:
        login_user(membership.member)
    flash('You have now joined ' + membership.organization.name, 'success')
    return membership
    
def create_shift(pos_key, assigned_user_id, day, start_time, end_time):
    """
    Creates a new shift object
    :param pos_key:
    :param assigned_user_id:
    :param day:
    :param start_time:
    :param end_time:
    :return:
    """
    # create shift with parameters
    shift = Shift(position_id=pos_key, assigned_user_id=assigned_user_id, day=day, start_time=start_time,
                    end_time=end_time)
    
    # add shift to database
    db.session.add(shift)
    db.session.commit()
    return shift
    
def gather_members_for_shift(org_key):
    """
    Creates a formatted list of users in an organization
    to use in ShiftForm.user
    :param org_key:
    :return:
    """
    # filter users by members of current org in current position
    eligible_members = Membership.query.filter_by(organization_id=org_key).all()
    # create list to fill in SelectField
    users = []
    users.append((None, '--'))
    for c in eligible_members:
        # use 'member' backref in user-membership relationship
        users.append((c.member.id, c.member.first_name + ' ' + c.member.last_name))
    
    return users

def update_shift(shift, pos_key, assigned_user_id, day, start_time, end_time):
    """
    Updates an existing shift
    :param shift:
    :param pos_key:
    :param assigned_user_id:
    :param day:
    :param start_time:
    :param end_time
    :return:
    """
    curr_shift = get_shift(shift.id)
    curr_shift.position_id = pos_key
    curr_shift.assigned_user_id = assigned_user_id
    curr_shift.day = day
    curr_shift.start_time = start_time
    curr_shift.end_time = end_time
    db.session.commit()





