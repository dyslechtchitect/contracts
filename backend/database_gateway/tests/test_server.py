import json
import uuid
from unittest.mock import patch, MagicMock
from flask import Flask, current_app
import pytest

from server import ContractsServer


@pytest.fixture
def app():
    app = Flask(__name__)
    return app


@pytest.fixture
def contracts_app(app):
    return MagicMock()


@pytest.fixture
def client(app, contracts_app):
    with app.test_request_context():
        yield ContractsServer(app, contracts_app)


def test_create_user(client):
    with patch('server.cognito_auth_required', MagicMock(return_value=lambda x: x)):
        expected_user_id = uuid.uuid4()
        expected_response = {"user_id": expected_user_id, "username": "test_username"}
        client._contracts_app.create_user.return_value = expected_response

        # Mock current_cognito_jwt
        current_cognito_jwt = {'sub': expected_user_id, 'username': 'test_username'}

        # Mock current_app.extensions['cognito_auth']
        current_app.extensions = {'cognito_auth': MagicMock(get_token=MagicMock(return_value="mock_token"))}

        with patch('server.current_cognito_jwt', current_cognito_jwt):
            response_dict = client.create_user()

        assert response_dict == expected_response
        client._contracts_app.create_user.assert_called_once_with(expected_user_id, "test_username")
