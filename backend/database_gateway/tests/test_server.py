import unittest
import uuid
from unittest.mock import patch, MagicMock
from datetime import datetime
import json

from flask import Flask
from sqlalchemy import create_engine
from werkzeug.datastructures import ImmutableMultiDict

from contracts_app import ContractsApp
from server import ContractsServer
from adapters.boto_adapter import BotoAdapter
from adapters.db_adapter import DbAdapter
from dto import UserDto
from db.models import Base, User
from db.crud.crud import CRUD


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

    def test_create_user(self):
        # Mock authentication decorator
        auth_decorator = MagicMock()
        auth_decorator.return_value = lambda func: func
        expected_user_id = str(uuid.uuid4())
        with patch('server.current_cognito_jwt', {'sub': expected_user_id, 'username': 'test_username'}), \
             self.app.test_request_context():
            # Mock cognito_auth extension and add it to the Flask application context
            self.app.extensions = {'cognito_auth': MagicMock(get_token=MagicMock(return_value="mock_token"))}

            with patch('server.cognito_auth_required', auth_decorator):
                # Make a POST request to create a user
                response = self.client.post('/user')

                # Assert that the BotoAdapter's get_user_data method is called with the correct username
                self.boto_adapter.get_user_data.assert_called_once_with('test_username')

                # Assert the status code and response data
                self.assertEqual(response.status_code, 200)
                self.assertEqual(expected_user_id, str(response.data.decode()))


    def tearDown(self):
        # Clean up the database session and connections
        self.engine.dispose()


if __name__ == '__main__':
    unittest.main()
