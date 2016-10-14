from functools import wraps
from flask import abort, render_template, g
from models import Organization


def owns_organization(fn):
    @wraps(fn)
    def decorated_view(*args, **kwargs):
        key = kwargs['key']
        org = Organization.query.filter_by(id=key).first()

        if org.owner.id != g.user.id:
            abort(render_template('errors/403_organization_owner.html'), 403)
        # Do something with value...
        if key == '2':
            abort(400)
        return fn(*args, **kwargs)
    return decorated_view
