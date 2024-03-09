import unittest
from functools import wraps
from importlib import reload
from unittest.mock import patch

import pytest

import contracts_app
import run_server
import server
from contracts_app import ContractsApp


def setUpModule():
    """
    Patches out the decorator (in the library) and reloads the module
    under test.
    """
    patch('flask_cognito.cognito_auth_required', mock_cognito_auth_required).start()
    reload(server)


@pytest.fixture()
def app():
    with run_server.Boiler.app.app_context():
        app_ = run_server.Boiler.app
        app_.config.update({
            "TESTING": True,
        })

    yield app_


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()


patch('server.current_cognito_jwt')


def mock_cognito_auth_required(fn):
    """
    This is a dummy wrapper of @cognito auth required, it passes-through
    to the
    wrapped fuction without performing any cognito logic.

    """

    @wraps(fn)
    def decorator(*args, **kwargs):
        return fn(*args, **kwargs)

    return decorator


@patch('server.current_cognito_jwt')
class TestContractApp(unittest.TestCase):
    def test_my_example_function(self, mock_current_cognito_jwt):
        mock_current_cognito_jwt.__getitem__.return_value = 'test'
        response = server.ContractsServer.create_user()
        self.assertEqual(response, {'your_sub': 'test'})



