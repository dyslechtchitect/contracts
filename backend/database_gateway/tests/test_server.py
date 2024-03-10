import json
import unittest
import uuid
from random import random
from unittest.mock import MagicMock

from sqlalchemy import create_engine
from flask import Flask

from contracts_app import ContractsApp
from dto import UserDto
from server import ContractsServer
from adapters.boto_adapter import BotoAdapter
from adapters.db_adapter import DbAdapter
from db.models import Base
from db.crud.crud import CRUD
from tests.test_utils import with_user_auth_context

# Global constants
TEST_USERNAME = 'test_username'
TEST_EMAIL = 'test_user@email.com'

CONTRACT_DATA = {"payment_terms": "Net 30", "delivery_terms": "FOB Destination"}
CREATOR_RELATIONSHIP_DATA = {
    "is_creator": True,
    "is_editor": True,
    "is_party": False,
    "is_signed": False,
    "date_signed": 'None'
}

GUEST_RELATIONSHIP_DATA = {
    "is_creator": False,
    "is_editor": False,
    "is_party": False,
    "is_signed": False,
    "date_signed": 'None'
}


class TestCreateUser(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.testing = True
        self.engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(self.engine)
        self.crud = CRUD(self.engine)
        self.boto_adapter = MagicMock(spec=BotoAdapter)
        self.db_adapter = DbAdapter(self.crud)
        self.contracts_app = ContractsApp(self.db_adapter, self.boto_adapter)
        self.client = self.app.test_client()
        self.server = ContractsServer(self.app, self.contracts_app)

    def tearDown(self):
        self.engine.dispose()

    def given_boto_returns(self, user_id: str, name='Test User', email='test@example.com'):
        self.boto_adapter.get_user_data.return_value = {'sub': user_id, 'name': name, 'email': email}

    def given_user_with_auth_context(self, user_id: str):
        self.given_boto_returns(user_id)
        self.client.post('/user')

    def given_user_in_db(self, user_dto: UserDto):
        self.contracts_app.db_adapter.create_user(user_dto)

    def given_contract_with_auth_context(self, data: dict) -> str:
        create_response = self.client.post('/contract', json={"data": data})
        return json.loads(create_response.data.decode())['contract_id']

    def given_contract_in_db(self, user_id: str, data: dict) -> str:
        return self.contracts_app.create_contract(user_id, data)

    def match_contracts_ignoring_dates(self, contract_a: dict, contract_b: dict):
        contract_a_filtered = {k: v for k, v in contract_a.items() if "date" not in k}
        contract_b_filtered = {k: v for k, v in contract_b.items() if "date" not in k}
        self.assertEqual(contract_a_filtered, contract_b_filtered)

    @with_user_auth_context
    def test_create_user(self, expected_user_id):
        self.given_boto_returns(expected_user_id)
        response = self.client.post('/user')
        self.boto_adapter.get_user_data.assert_called_once_with(TEST_USERNAME)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(expected_user_id, response.data.decode())

    @with_user_auth_context
    def test_get_user(self, expected_user_id):
        expected_user = UserDto(expected_user_id, TEST_USERNAME, TEST_EMAIL, {str(random()): str(random())})
        self.given_user_in_db(expected_user)
        response_get_user = self.client.get('/user')
        self.assertEqual(response_get_user.status_code, 200)
        self.assertEqual(json.loads(expected_user.as_json()), json.loads(response_get_user.data.decode()))

    @with_user_auth_context
    def test_create_contract(self, expected_user_id):
        expected_user = UserDto(expected_user_id, TEST_USERNAME, TEST_EMAIL, {str(random()): str(random())})
        self.given_user_in_db(expected_user)
        response = self.client.post('/contract',
                                    json={"data": CONTRACT_DATA})
        self.assertEqual(response.status_code, 201)

    @with_user_auth_context
    def test_get_contract(self, expected_user_id):
        expected_data = {'data': CONTRACT_DATA}
        expected_relationship = {"user_id": expected_user_id, **CREATOR_RELATIONSHIP_DATA}
        expected_user = UserDto(expected_user_id, TEST_USERNAME, TEST_EMAIL, {str(random()): str(random())})
        self.given_user_in_db(expected_user)
        contract_id = self.given_contract_in_db(expected_user_id, expected_data)
        expected_contract = {'id': contract_id, 'data': expected_data['data'], 'relationships': [expected_relationship]}
        response = self.client.get(f'/contract/{contract_id}')
        actual_contract = json.loads(response.data.decode())
        self.match_contracts_ignoring_dates(actual_contract, expected_contract)

    @with_user_auth_context
    def test_list_contracts(self, expected_user_id):
        expected_data = {'data': CONTRACT_DATA}
        expected_user = UserDto(expected_user_id, TEST_USERNAME, TEST_EMAIL, {str(random()): str(random())})
        self.given_user_in_db(expected_user)
        contract_id_1 = self.given_contract_in_db(expected_user_id, expected_data)
        contract_id_2 = self.given_contract_in_db(expected_user_id, expected_data)
        expected_ids = [contract_id_1, contract_id_2]
        response = self.client.get(f'/user/contracts')
        self.assertEqual(response.status_code, 200)
        actual_ids = json.loads(response.data.decode())
        self.assertCountEqual(actual_ids, expected_ids)

    @with_user_auth_context
    def test_share_contract(self, expected_user_id):
        guest_user_id = str(uuid.uuid4())
        expected_data = {'data': CONTRACT_DATA}
        expected_relationships = [
            {"user_id": expected_user_id, **CREATOR_RELATIONSHIP_DATA},
            {'user_id': guest_user_id, 'date_signed': 'None', **GUEST_RELATIONSHIP_DATA}
        ]
        self.given_user_with_auth_context(expected_user_id)
        contract_id = self.given_contract_with_auth_context(expected_data['data'])
        expected_contract = {'id': contract_id, 'data': expected_data['data'], 'relationships': expected_relationships}
        guest_email = f"{random()}@email.com"
        guest_user = UserDto(guest_user_id, "guest_username", guest_email, {str(random()): str(random())})
        self.given_user_in_db(guest_user)

        # Share the contract
        share_response = self.client.post(f'/contract/{contract_id}', json={"email": guest_email})
        self.assertEqual(share_response.status_code, 201)

        # Retrieve the contract
        get_response = self.client.get(f'/contract/{contract_id}')
        self.assertEqual(get_response.status_code, 200)
        actual_contract = json.loads(get_response.data.decode())

        # Assert the contract details
        self.match_contracts_ignoring_dates(actual_contract, expected_contract)
