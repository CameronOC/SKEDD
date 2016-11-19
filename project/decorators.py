# project/decorators.py


from functools import wraps

from flask import flash, redirect, url_for, abort, render_template, g
from flask_login import current_user

from models import Organization, Membership, Shift
from exceptions import NotOwner, NotMember, ShiftNotInOrg


def check_confirmed(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if current_user.confirmed is False:
            flash('Please confirm your account!', 'warning')
            return redirect(url_for('user.unconfirmed'))
        return func(*args, **kwargs)

    return decorated_function


def owns_organization(fn):
    @wraps(fn)
    def decorated_view(*args, **kwargs):
        key = kwargs['key']
        org = Organization.query.filter_by(id=key).first()

        if org.owner.id != g.user.id:
            raise NotOwner('403 Access Denied. You must own this organization.', status_code=403)
        return fn(*args, **kwargs)
    return decorated_view


def admin_of_org(fn):
    @wraps(fn)
    def decorated_func(*args, **kwargs):
        key = kwargs['key']
        membership = Membership.query.filter_by(member_id=g.user.id, organization_id=key).first()

        if membership is None:
            raise NotMember('403 Access Denied. You must be a member of this organization.', status_code=403)
        return fn(*args, **kwargs)
    return decorated_func


def organization_member(fn):
    @wraps(fn)
    def decorated_view(*args, **kwargs):
        key = kwargs['key']
        membership = Membership.query.filter_by(member_id=g.user.id, organization_id=key).first()

        if membership is None:
            raise NotMember('403 Access Denied. You must be a member of this organization.', status_code=403)
        return fn(*args, **kwargs)
    return decorated_view

def shift_belongs_to_org(fn):
    @wraps(fn)
    def decorated_view(*args, **kwargs):
        key = kwargs['key']
        key1 = kwargs['key1']

        shift = Shift.query.get(key1)
        if shift is None or shift.Position.organization_id != key:
            raise ShiftNotInOrg('400 Bad Request. No such Shift for this Organization', status_code=404)
        return fn(*args, **kwargs)
    return decorated_view
