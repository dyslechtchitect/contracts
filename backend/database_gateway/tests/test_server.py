import json
import uuid
from unittest.mock import patch, MagicMock
from flask import Flask, current_app
import pytest
from sqlalchemy import create_engine

from adapters.boto_adapter import BotoAdapter
from adapters.db_adapter import DbAdapter
from contracts_app import ContractsApp
from db.crud.crud import CRUD
from db.models import Base
from server import ContractsServer


@pytest.fixture
def app():
    app = Flask(__name__)
    return app



mock_boto_adapter = MagicMock(spec=BotoAdapter)

@pytest.fixture
def contracts_app(app):
    engine = create_engine('sqlite:///:memory:', echo=False)
    Base.metadata.create_all(engine)
    crud = CRUD(engine)
    db_adapter = DbAdapter(crud)
    return ContractsApp(db_adapter, mock_boto_adapter)


@pytest.fixture
def client(app, contracts_app):
    with app.test_request_context():
        yield ContractsServer(app, contracts_app)


def test_create_user(client):
    with patch('server.cognito_auth_required', MagicMock(return_value=lambda x: x)):
        expected_user_id = str(uuid.uuid4())
        expected_response = {"user_id": expected_user_id, "username": "test_username"}
        given_boto_Returns(expected_user_id, "username", "user@email.com")
        # Mock current_cognito_jwt
        current_cognito_jwt = {'sub': expected_user_id, 'username': 'test_username'}

        # Mock current_app.extensions['cognito_auth']
        current_app.extensions = {'cognito_auth': MagicMock(get_token=MagicMock(return_value="mock_token"))}

        with patch('server.current_cognito_jwt', current_cognito_jwt):
            # Adjusted call with appropriate arguments
            response_id = client._contracts_app.create_user(expected_user_id, "test_username")

        assert response_id == expected_user_id

def given_boto_Returns(user_id:str, username: str, email: str):
    mock_boto_adapter.get_user_data.return_value = {'sub': user_id, 'name': username, 'email': email, 'data': {}}