# project/main/views.py


#################
#### imports ####
#################

from flask import render_template, Blueprint, request, session, g, redirect, url_for
from source import app, db
from flask_login import login_required
from forms import CreateForm

from models import User, Organization, Position

################
#    config    #
################

main_blueprint = Blueprint('main', __name__, )


@app.before_request
def load_user():
    if 'user_id' in session:
        if session["user_id"]:
            user = User.query.filter_by(id=session["user_id"]).first()
        else:
            user = {"email": "Guest"}  # Make it better, use an anonymous User instead
    else:
        user = {"email": "Guest"}  # Make it better, use an anonymous User instead

    g.user = user


################
#    routes    #
################

@main_blueprint.route('/')
def landing():
    return render_template('main/index.html')


@main_blueprint.route('/home', methods=['GET', ])
@login_required
def home():
    orgs = g.user.orgs_owned.all()

    return render_template('main/home.html', organizations=orgs)


@main_blueprint.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'GET':
        return render_template('main/create.html', form=CreateForm())
    else:
        name = request.form['name']
        owner = g.user

        org = Organization(name=name, owner=owner)

        db.session.add(org)
        db.session.commit()

        return redirect('/organization/' + str(org.id))


@main_blueprint.route('/organization/<key>', methods=['GET', ])
@login_required
def organization(key):
    org = Organization.query.filter_by(id=key).first()

    if org.owner.id != g.user.id:
        return render_template('errors/403_organization.html'), 403

    return render_template('main/organization.html', organization=org)


@main_blueprint.route('/organization/<key>/position/<key2>', methods={'GET', })
@login_required
def position(key, key2):
    org = Organization.query.filter_by(id=key).first()

    if org.owner.id != g.user.id:
        return render_template('errors/403_organization.html'), 403

    pos = Position.query.filter_by(id=key2).first()
    return render_template('main/position.html', position=pos)


@main_blueprint.route('/organization/<key>/create_position', methods=['GET', 'POST'])
@login_required
def create_position(key):
    if request.method == 'GET':
        org = Organization.query.filter_by(id=key).first()

        if org.owner.id != g.user.id:
            return render_template('errors/403_organization.html'), 403

        return render_template('main/create_position.html', form=CreateForm())
    else:
        org = Organization.query.filter_by(id=key).first()

        if org.owner.id != g.user.id:
            return render_template('errors/403_organization.html'), 403

        title = request.form['name']
        pos = Position(title=title, organization_id=org.id)
        db.session.add(pos)
        org.owned_positions.append(pos)
        db.session.commit()

        return redirect('/organization/' + str(org.id) + '/position/' + str(pos.id))
