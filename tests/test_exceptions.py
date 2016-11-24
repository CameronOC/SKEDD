from project import app, exceptions, db
from flask_testing import TestCase
from base_test import BaseTest
from flask_login import login_user
import json
import project.models as models

class ExceptionTest(TestCase):

    def create_app(self):
        app.config.from_object('project.config.TestingConfig')
        return app

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def tearDown(self):
        pass

    def test_notowner(self):
        try:
            raise exceptions.NotOwner
        except exceptions.NotOwner as exception:
            result = exception.to_dict()
            assert 'status' in result
            assert result['status'] == 'error'
            assert 'message' in result
            assert result['message'] == '403 Access Denied. You must own this organization.'
            assert exception.status_code == 403
            assert exception.message == None

    def test_notowner_custom(self):
        try:
            raise exceptions.NotOwner(message='custom', status_code=1)
        except exceptions.NotOwner as exception:
            result = exception.to_dict()
            assert 'status' in result
            assert result['status'] == 'error'
            assert 'message' in result
            assert result['message'] == 'custom'
            assert exception.status_code == 1
            assert exception.message == 'custom'

    def test_notmember(self):
        try:
            raise exceptions.NotMember
        except exceptions.NotMember as exception:
            result = exception.to_dict()
            assert 'status' in result
            assert result['status'] == 'error'
            assert 'message' in result
            assert result['message'] == '403 Access Denied. You must be a member of this organization.'
            assert exception.status_code == 403
            assert exception.message == None

    def test_notmember_custom(self):
        try:
            raise exceptions.NotMember(message='custom', status_code=1)
        except exceptions.NotMember as exception:
            result = exception.to_dict()
            assert 'status' in result
            assert result['status'] == 'error'
            assert 'message' in result
            assert result['message'] == 'custom'
            assert exception.status_code == 1
            assert exception.message == 'custom'

    def test_notadmin(self):
        try:
            raise exceptions.NotAdmin
        except exceptions.NotAdmin as exception:
            result = exception.to_dict()
            assert 'status' in result
            assert result['status'] == 'error'
            assert 'message' in result
            assert result['message'] == '403 Access Denied. You must be an admin of this organization.'
            assert exception.status_code == 403
            assert exception.message == None

    def test_notadmin_custom(self):
        try:
            raise exceptions.NotAdmin(message='custom', status_code=1)
        except exceptions.NotAdmin as exception:
            result = exception.to_dict()
            assert 'status' in result
            assert result['status'] == 'error'
            assert 'message' in result
            assert result['message'] == 'custom'
            assert exception.status_code == 1
            assert exception.message == 'custom'

    def test_shiftnotinorg(self):
        try:
            raise exceptions.ShiftNotInOrg
        except exceptions.ShiftNotInOrg as exception:
            result = exception.to_dict()
            assert 'status' in result
            assert result['status'] == 'error'
            assert 'message' in result
            assert result['message'] == '400 Bad Request. No such Shift for this Organization'
            assert exception.status_code == 403
            assert exception.message == None

    def test_shiftnotinorg_custom(self):
        try:
            raise exceptions.ShiftNotInOrg(message='custom', status_code=1)
        except exceptions.ShiftNotInOrg as exception:
            result = exception.to_dict()
            assert 'status' in result
            assert result['status'] == 'error'
            assert 'message' in result
            assert result['message'] == 'custom'
            assert exception.status_code == 1
            assert exception.message == 'custom'


class TestOrganization(BaseTest, TestCase):

    def login(self, email, password):
        return self.client.post('/login', data=dict(
            email=email,
            password=password
        ), follow_redirects=True)

    def logout(self):
        return self.client.get('/logout', follow_redirects=True)


    def test_notowner_html(self):
        """
        Test an endpoint with organization owner protection and html response
        :return:
        """
        rv = self.login(self.john.email, 'password')
        self.assertEquals(rv.status_code, 200)

        result = self.client.post('/organization/1/shift/create', follow_redirects=True,
                                  headers={'Accept': 'text/html'})
        print result.status_code
        print result.data
        self.assertEquals(result.status_code, 403)

        rv = self.logout()
        self.assertEquals(rv.status_code, 200)

    def test_notowner_json(self):
        """

        :return:
        """
        rv = self.login(self.john.email, 'password')
        self.assertEquals(rv.status_code, 200)

        result = self.client.post('/organization/' + str(self.organization.id) + '/shift/create',
                                  follow_redirects=True,
                                  headers={'Accept': 'application/json'})

        self.assertEquals(result.status_code, 200)

        json_data =  json.loads(result.data)

        assert 'status' in json_data
        assert json_data['status'] == 'error'
        assert 'message' in json_data
        assert json_data['message'] == '403 Access Denied. You must own this organization.'

        rv = self.logout()
        self.assertEquals(rv.status_code, 200)


    def test_notmember_html(self):
        """
        Test an endpoint with organization owner protection and html response
        :return:
        """

        user = models.User(first_name='not',
                           last_name='Member',
                           email='not@member.com',
                           password='password',
                           confirmed=True)
        db.session.add(user)
        db.session.commit()

        rv = self.login(user.email, 'password')
        self.assertEquals(rv.status_code, 200)

        result = self.client.get('/organization/' + str(self.organization.id),
                                  follow_redirects=True,
                                 headers={'Accept': 'text/html'})
        print result.status_code
        print result.data
        self.assertEquals(result.status_code, 403)

        rv = self.logout()
        self.assertEquals(rv.status_code, 200)

    def test_notmember_json(self):
        """

        :return:
        """
        user = models.User(first_name='not',
                           last_name='Member',
                           email='not@member.com',
                           password='password',
                           confirmed=True)
        db.session.add(user)
        db.session.commit()
        rv = self.login(user.email, 'password')
        self.assertEquals(rv.status_code, 200)

        result = self.client.get('/organization/' + str(self.organization.id),
                                  follow_redirects=True,
                                  headers={'Accept': 'application/json'})

        self.assertEquals(result.status_code, 200)

        json_data =  json.loads(result.data)

        assert 'status' in json_data
        assert json_data['status'] == 'error'
        assert 'message' in json_data
        assert json_data['message'] == '403 Access Denied. You must be a member of this organization.'

        rv = self.logout()
        self.assertEquals(rv.status_code, 200)
