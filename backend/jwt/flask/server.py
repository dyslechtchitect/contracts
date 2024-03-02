# configuration
from flask import Flask
from flask_cognito import cognito_auth_required, current_user, current_cognito_jwt
from flask import jsonify
from flask_cognito import CognitoAuth

app = Flask(__name__)
# initialize extension

# cogauth = CognitoAuth(app)

app.config.update({
    'COGNITO_REGION': 'eu-north-1',
    'COGNITO_USERPOOL_ID': 'eu-north-1_Ia3PeTo0f',

    # optional
    'COGNITO_APP_CLIENT_ID': '4gi33ef3i1cm3s39mob5gcmn56',  # client ID you wish to verify user is authenticated against
    'COGNITO_CHECK_TOKEN_EXPIRATION': False,  # disable token expiration checking for testing purposes
    'COGNITO_JWT_HEADER_NAME': 'Authorization',
    'COGNITO_JWT_HEADER_PREFIX': 'Bearer',
    'AWS_COGNITO_REDIRECT_URL' : 'http://localhost:5000/postlogin'
})
CognitoAuth(app)

@app.route('/access')
@cognito_auth_required
def api_private():
    # user must have valid cognito access or ID token in header
    # (accessToken is recommended - not as much personal information contained inside as with idToken)
    return jsonify({
        'cognito_sub': str(current_cognito_jwt['sub']),  # from cognito pool
        'jwt': str(current_cognito_jwt),  # from your database
    })
