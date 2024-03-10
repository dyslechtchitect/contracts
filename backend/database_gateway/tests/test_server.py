import json
import unittest

from sqlalchemy import create_engine

from contracts_app import ContractsApp
from server import ContractsServer
from adapters.boto_adapter import BotoAdapter
from adapters.db_adapter import DbAdapter
from db.models import Base
from db.crud.crud import CRUD
from flask import Flask
from unittest.mock import MagicMock

from tests.test_utils import with_server_context


class TestCreateUser(unittest.TestCase):
    def setUp(self):
        # Create a Flask app and configure it
        self.app = Flask(__name__)
        self.app.testing = True

        # Create an in-memory SQLite database
        self.engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(self.engine)
        self.crud = CRUD(self.engine)

        # Create mock BotoAdapter
        self.boto_adapter = MagicMock(spec=BotoAdapter)

        # Create the ContractsApp instance
        self.db_adapter = DbAdapter(self.crud)
        self.contracts_app = ContractsApp(self.db_adapter, self.boto_adapter)

        # Create a test client
        self.client = self.app.test_client()

        # Create the ContractsServer instance
        self.server = ContractsServer(self.app, self.contracts_app)

    def tearDown(self):
        # Clean up the database session and connections
        self.engine.dispose()

    def given_boto_returns(self, user_id: str, name='Test User', email='test@example.com'):
        self.boto_adapter.get_user_data.return_value = {
            'sub': user_id,
            'name': name,
            'email': email
        }

    @with_server_context
    def given_user(self, user_id: str, expected_user_email: str):
        self.given_boto_returns(user_id)
        response = self.client.post('/user')
        # Assert the status code of the response for creating user
        self.assertEqual(response.status_code, 200)

    def given_contract(self, data: dict) -> str:
        create_response = self.client.post('/contract', json={
            "data": data
        })
        self.assertEqual(create_response.status_code, 201)
        return json.loads(create_response.data.decode())['contract_id']

    @with_server_context
    def test_create_user(self, expected_user_id, _):
        # Make a POST request to create a user
        self.given_boto_returns(expected_user_id)
        response = self.client.post('/user')
        # Assert that the BotoAdapter's get_user_data method is called with the correct username
        self.boto_adapter.get_user_data.assert_called_once_with('test_username')

        # Assert the status code of the response
        self.assertEqual(response.status_code, 200)
        # Assert that the response data matches the expected user ID
        self.assertEqual(expected_user_id, response.data.decode())

    @with_server_context
    def test_get_user(self, expected_user_id, _):
        # Make a POST request to create a user
        self.given_user(expected_user_id)

        # Assert that the BotoAdapter's get_user_data method is called with the correct username
        self.boto_adapter.get_user_data.assert_called_once_with('test_username')

        # Make a GET request to fetch user data
        response_get_user = self.client.get('/user')

        # Assert the status code of the response for getting user data
        self.assertEqual(response_get_user.status_code, 200)

        # Assert that the response data contains the expected user ID
        self.assertEqual(expected_user_id, json.loads(response_get_user.data.decode())['id'])

    @with_server_context
    def test_create_contract(self, expected_user_id, _):
        # Make a POST request to create a user
        self.given_user(expected_user_id)
        response = self.client.post('/contract', json={
            "data": {
                "payment_terms": "Net 30",
                "delivery_terms": "FOB Destination"
            }
        })
        # Assert the status code of the response for getting user data
        self.assertEqual(response.status_code, 201)

    @with_server_context
    def test_get_contract(self, expected_user_id, _):
        # Make a POST request to create a user
        expected_data = {
            "payment_terms": "Net 30",
            "delivery_terms": "FOB Destination"
        }

        expected_relationship = {
            "user_id": expected_user_id,
            "is_creator": True,
            "is_editor": True,
            "is_party": False,
            "is_signed": False,
            "date_signed": 'None'
        }

        self.given_user(expected_user_id)
        contract_id = self.given_contract(expected_data)
        # Assert the status code of the response for getting user data
        response = self.client.get(f'/contract/{contract_id}')

        actual_data = json.loads(response.data.decode())['data']
        actual_relationship = json.loads(response.data.decode())['relationships'][0]

        self.assertEqual(actual_data, expected_data)
        self.assertEqual(actual_relationship, expected_relationship)



    @with_server_context
    def test_list_contracts(self, expected_user_id, _email, *args):
        # Make a POST request to create a user
        expected_data = {
            "payment_terms": "Net 30",
            "delivery_terms": "FOB Destination"
        }

        self.given_user(expected_user_id, _email)
        contract_id_1 = self.given_contract(expected_data)
        contract_id_2 = self.given_contract(expected_data)
        expected_ids = [contract_id_1, contract_id_2]
        # Assert the status code of the response for getting user data
        response = self.client.get(f'/user/contracts')
        self.assertEqual(response.status_code, 200)
        actual_ids = json.loads(response.data.decode())

        self.assertCountEqual(actual_ids, expected_ids)


if __name__ == '__main__':
    unittest.main()
