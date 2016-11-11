# project/decorators.py


from functools import wraps

from flask import flash, redirect, url_for, abort, render_template, g
from flask_login import current_user

from models import Organization



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
        print key
        org = Organization.query.filter_by(id=key).first()

        if org.owner.id != g.user.id:
            abort(render_template('errors/403_organization_owner.html'), 403)
        return fn(*args, **kwargs)
    return decorated_view
