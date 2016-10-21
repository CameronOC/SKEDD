import datetime
from project import db, bcrypt
from project.models import Organization, User, Membership
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