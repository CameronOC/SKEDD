from flask import render_template, jsonify
from project import app
from flask import request

def request_wants_json():
    best = request.accept_mimetypes \
        .best_match(['application/json', 'text/html'])
    return best == 'application/json' and \
        request.accept_mimetypes[best] > \
        request.accept_mimetypes['text/html']


class NotOwner(Exception):
    status_code = 403

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['status'] = 'error'
        rv['message'] = self.message or '403 Access Denied. You must own this organization.'
        return rv


class NotMember(Exception):
    status_code = 403

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['status'] = 'error'
        rv['message'] = self.message or '403 Access Denied. You must be a member of this organization.'
        return rv


@app.errorhandler(NotOwner)
def handle_invalid_usage(error):
    if request_wants_json():
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response
    else:
        return render_template('errors/403_organization_owner.html'), 403

@app.errorhandler(NotMember)
def handle_invalid_usage(error):
    if request_wants_json():
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response
    else:
        return render_template('errors/403_organization_member.html'), 403