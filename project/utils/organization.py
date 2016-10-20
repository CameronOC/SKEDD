from project import db
from project.models import Organization, User, Membership
from project.email import send_email
from project.utils.token import confirm_token, generate_invitation_token

from flask import render_template, flash, url_for

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


def get_organization(id):
    """
    gets an organization by id and returns the object or None
    if it doesn't exist
    :param id:
    :return:
    """
    return Organization.query.get(id)


def is_in_org(org, user):
    """
    Checks if a user is in an organization
    :param organization_id:
    :param user_id:
    :return:
    """
    membership = Membership.query.filter_by(member_id=user.id, organization_id=org.id).first()

    if membership is not None:
        return True
    return False


def invite_member(org, invite_form):
    """
    Invite a user to the organization id, creating a dummy account if needed
    :param organization_id:
    :return:
    """
    user = User.query.filter_by(email=email.data).first()

    if user is None:
        user = User(
            first_name=first_name.data,
            last_name=last_name.data,
            email=email.data,
            password="temp",
            confirmed=False
        )
        db.session.add(user)

    db.session.commit()

    if is_in_org(org, user):
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