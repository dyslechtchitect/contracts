# configuration
from flask import Flask
from flask_cognito import cognito_auth_required, current_cognito_jwt
from flask import jsonify
from flask_cognito import CognitoAuth
from sqlalchemy import create_engine

from db.models import Base
from db.crud import CRUD
from dto import UserDto

app = Flask(__name__)
# initialize extension



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

cogauth = CognitoAuth(app)
engine = create_engine('sqlite:///db.db')  # connect to server
Base.metadata.create_all(engine)
crud = CRUD(engine)


@app.route('/access')
@cognito_auth_required
def create_user():
    # user must have valid cognito access or ID token in header
    # (accessToken is recommended - not as much personal information contained inside as with idToken)
    user = UserDto(id=current_cognito_jwt['sub'],
                   name=current_cognito_jwt['cognito:username'],
                   email=current_cognito_jwt['email'],
                   data={}
                   )
    crud.create_user(user)
    return jsonify({
        'cognito_sub': str(current_cognito_jwt['sub']),  # from cognito pool
        'jwt': str(current_cognito_jwt),  # from your database
    })



