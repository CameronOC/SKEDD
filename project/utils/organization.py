from project import db
from project.models import Organization, User, Membership


def create_organization(name, owner_id):
    """
    Creates a new organization with paramaters and returns the created
    organization object
    :param owner_id:
    :param name:
    :return:
    """
    org = Organization(name, owner_id)
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