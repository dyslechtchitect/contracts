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
        self.boto_adapter.get_user_data.return_value = {
            'sub': 'test_user_id',
            'name': 'Test User',
            'email': 'test@example.com'
        }

        # Create the ContractsApp instance
        self.db_adapter = DbAdapter(self.crud)
        self.contracts_app = ContractsApp(self.db_adapter, self.boto_adapter)

        # Create a test client
        self.client = self.app.test_client()

        # Create the ContractsServer instance
        self.server = ContractsServer(self.app, self.contracts_app)

    @with_server_context
    def test_create_user(self, expected_user_id):
        # Make a POST request to create a user
        response = self.client.post('/user')

        # Assert that the BotoAdapter's get_user_data method is called with the correct username
        self.boto_adapter.get_user_data.assert_called_once_with('test_username')

        # Assert the status code of the response
        self.assertEqual(response.status_code, 200)
        # Assert that the response data matches the expected user ID
        self.assertEqual(expected_user_id, response.data.decode())


    def tearDown(self):
        # Clean up the database session and connections
        self.engine.dispose()


if __name__ == '__main__':
    unittest.main()
