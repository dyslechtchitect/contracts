import json
import unittest
import uuid
from random import random

from sqlalchemy import create_engine

from contracts_app import ContractsApp
from dto import UserDto
from server import ContractsServer
from adapters.boto_adapter import BotoAdapter
from adapters.db_adapter import DbAdapter
from db.models import Base
from db.crud.crud import CRUD
from flask import Flask
from unittest.mock import MagicMock

from tests.test_utils import with_user_auth_context


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

    def given_user(self, user_id: str):
        self.given_boto_returns(user_id)
        response = self.client.post('/user')
        # Assert the status code of the response for creating user
        self.assertEqual(response.status_code, 200)

    def given_user_in_db(self, user_dto: UserDto):
        self.contracts_app.db_adapter.create_user(user_dto)

    def given_contract(self, data: dict) -> str:
        create_response = self.client.post('/contract', json={
            "data": data
        })
        self.assertEqual(create_response.status_code, 201)
        return json.loads(create_response.data.decode())['contract_id']

    def given_contract_in_db(self, user_id: str, data: dict) -> str:
        contract_id = self.contracts_app.create_contract(user_id, data)
        return contract_id

    def match_contracts_ignoring_date(self, contract_a: dict, contract_b: dict):
        contract_a_filtered = {k: v for k, v in contract_a.items() if "date" not in k}
        contract_b_filtered = {k: v for k, v in contract_b.items() if "date" not in k}
        self.assertEqual(contract_a_filtered, contract_b_filtered)

    @with_user_auth_context
    def test_create_user(self, expected_user_id):
        # Make a POST request to create a user
        self.given_boto_returns(expected_user_id)
        response = self.client.post('/user')
        # Assert that the BotoAdapter's get_user_data method is called with the correct username
        self.boto_adapter.get_user_data.assert_called_once_with('test_username')

        # Assert the status code of the response
        self.assertEqual(response.status_code, 200)
        # Assert that the response data matches the expected user ID
        self.assertEqual(expected_user_id, response.data.decode())

    @with_user_auth_context
    def test_get_user(self, expected_user_id):
        # Make a POST request to create a user
        username = 'test_username'
        expected_user = UserDto(expected_user_id, username, "test_user@email.com", {str(random()): str(random())})
        self.given_user_in_db(expected_user)

        # Make a GET request to fetch user data
        response_get_user = self.client.get('/user')

        # Assert the status code of the response for getting user data
        self.assertEqual(response_get_user.status_code, 200)

        # Assert that the response data contains the expected user ID
        self.assertEqual(json.loads(expected_user.as_json()), json.loads(response_get_user.data.decode()))

    @with_user_auth_context
    def test_create_contract(self, expected_user_id):
        # Make a POST request to create a user
        expected_user = UserDto(expected_user_id, "test_username", "test_user@email.com",
                                {str(random()): str(random())})
        self.given_user_in_db(expected_user)
        response = self.client.post('/contract', json={
            "data": {
                "payment_terms": "Net 30",
                "delivery_terms": "FOB Destination"
            }
        })
        # Assert the status code of the response for getting user data
        self.assertEqual(response.status_code, 201)

    @with_user_auth_context
    def test_get_contract(self, expected_user_id):
        # Make a POST request to create a user
        expected_data = {'data': {
            "payment_terms": "Net 30",
            "delivery_terms": "FOB Destination"}
        }

        expected_relationship = {
            "user_id": expected_user_id,
            "is_creator": True,
            "is_editor": True,
            "is_party": False,
            "is_signed": False,
            "date_signed": 'None'
        }

        expected_user = UserDto(expected_user_id, "test_username", "test_user@email.com",
                                {str(random()): str(random())})
        self.given_user_in_db(expected_user)

        contract_id = self.given_contract_in_db(expected_user_id, expected_data)
        expected_contract = {
            'id': contract_id,
            'data': expected_data['data'],
            'relationships': [expected_relationship]
        }
        # Assert the status code of the response for getting user data
        response = self.client.get(f'/contract/{contract_id}')

        actual_contract = json.loads(response.data.decode())

        self.match_contracts_ignoring_date(actual_contract, expected_contract)

    @with_user_auth_context
    def test_list_contracts(self, expected_user_id):
        # Make a POST request to create a user
        expected_data = {'data': {
            "payment_terms": "Net 30",
            "delivery_terms": "FOB Destination"}
        }

        expected_user = UserDto(expected_user_id, "test_username", "test_user@email.com",
                                {str(random()): str(random())})
        self.given_user_in_db(expected_user)

        contract_id_1 = self.given_contract_in_db(expected_user_id, expected_data)
        contract_id_2 = self.given_contract_in_db(expected_user_id, expected_data)

        expected_ids = [contract_id_1, contract_id_2]
        # Assert the status code of the response for getting user data
        response = self.client.get(f'/user/contracts')
        self.assertEqual(response.status_code, 200)
        actual_ids = json.loads(response.data.decode())

        self.assertCountEqual(actual_ids, expected_ids)

    @with_user_auth_context
    def test_share_contract(self, expected_user_id):
        # Make a POST request to create a user
        guest_user_id = str(uuid.uuid4())
        expected_data = {'data': {
            "payment_terms": "Net 30",
            "delivery_terms": "FOB Destination"}
        }

        expected_relationships = [{
            "user_id": expected_user_id,
            "is_creator": True,
            "is_editor": True,
            "is_party": False,
            "is_signed": False,
            "date_signed": 'None'},
            {'date_signed': 'None',
             'is_creator': False,
             'is_editor': False,
             'is_party': False,
             'is_signed': False,
             'user_id': guest_user_id}
        ]

        self.given_user(expected_user_id)

        contract_id = self.given_contract(expected_data['data'])

        expected_contract = {
            'id': contract_id,
            'data': expected_data['data'],
            'relationships': expected_relationships
        }

        guest_email = f"{random()}@email.com"
        guest_user = UserDto(guest_user_id, "guest_username", guest_email,
                             {str(random()): str(random())})

        self.given_user_in_db(guest_user)

        self.client.post(f'/contract/{contract_id}', json={
            "email": guest_email

        })
        # Assert the status code of the response for getting user data
        response = self.client.get(f'/contract/{contract_id}')

        actual_contract = json.loads(response.data.decode())

        self.match_contracts_ignoring_date(actual_contract, expected_contract)


if __name__ == '__main__':
    unittest.main()
