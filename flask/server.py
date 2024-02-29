from flask import Flask
from flask_cognito import CognitoAuth, cognito_auth_required, current_user, current_cognito_jwt
import jsonify
app = Flask(__name__)
# configuration
app.config.update({
    'COGNITO_REGION': 'eu-north-1',
    'COGNITO_USERPOOL_ID': 'eu-north-1_T3kQIIhDp',

    # optional
    'COGNITO_APP_CLIENT_ID': '58ddlbqvo4ck1eks5t44rnhk0a',  # client ID you wish to verify user is authenticated against
    'COGNITO_CHECK_TOKEN_EXPIRATION': False,  # disable token expiration checking for testing purposes
    'COGNITO_JWT_HEADER_NAME': 'X-Contracts-Authorization',
    'COGNITO_JWT_HEADER_PREFIX': 'Bearer',
})



# initialize extension
from flask_cognito import CognitoAuth
cogauth = CognitoAuth(app)

@cogauth.identity_handler
def lookup_cognito_user(payload):
    """Look up user in our database from Cognito JWT payload."""
    # return User.query.filter(User.cognito_username == payload['username']).one_or_none()
    return True
@app.route('/api/private')
@cognito_auth_required
def api_private():
    # user must have valid cognito access or ID token in header
    # (accessToken is recommended - not as much personal information contained inside as with idToken)
    print(current_cognito_jwt)
    return jsonify({

        'cognito_username': current_cognito_jwt['username'],   # from cognito pool
        'user_id': current_user.id,   # from your database
    })