import uuid
from functools import wraps
from random import random
from unittest.mock import MagicMock, patch


def with_server_context(test_func):
    @wraps(test_func)
    def wrapper(self, *args, **kwargs):
        # Mock authentication decorator
        auth_decorator = MagicMock()
        auth_decorator.return_value = lambda func: func

        # Generate a random user ID
        expected_user_id = str(uuid.uuid4())
        expected_user_email = f"{random()}@email.com"

        with patch('server.current_cognito_jwt', {'sub': expected_user_id,
                                                  'username': 'test_username',
                                                  'email': expected_user_email}), \
                self.app.test_request_context():
            # Mock cognito_auth extension and add it to the Flask application context
            self.app.extensions = {'cognito_auth': MagicMock(get_token=MagicMock(return_value="mock_token"))}

            with patch('server.cognito_auth_required', auth_decorator):
                # Call the original test function with the necessary context
                test_func(self, expected_user_id, expected_user_email, *args, **kwargs)

    return wrapper
