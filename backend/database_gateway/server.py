# configuration
from uuid import UUID

from flask import Flask, session, request, redirect, url_for
from flask_cognito import cognito_auth_required, current_cognito_jwt
from flask import jsonify
from flask_cognito import CognitoAuth
from sqlalchemy import create_engine
from os import environ, path, urandom

from db.models import Base
from db.crud import CRUD
from dto import UserDto
from flask_cognito_lib import CognitoAuth as CognitoLibAuth
from flask_cognito_lib.decorators import (
    auth_required,
    cognito_login,
    cognito_login_callback,
    cognito_logout,
)
from flask_cognito_lib.exceptions import (
    AuthorisationRequiredError,
    CognitoGroupRequiredError,
)
import boto3


class Config:
    # General Config
    SECRET_KEY = environ.get("SECRET_KEY", urandom(32))
    FLASK_APP = "TEST_APP"
    FLASK_ENV = "TESTING"
    # config for flask-cognito
    COGNITO_REGION = 'eu-north-1'
    COGNITO_USERPOOL_ID = 'eu-north-1_5iTqlVssB'
    COGNITO_APP_CLIENT_ID = '6ovdonvgan55qqaiql0l5a4bnn'
    COGNITO_CHECK_TOKEN_EXPIRATION = False  # disable token expiration checking for testing purposes
    COGNITO_JWT_HEADER_NAME = 'Authorization'
    COGNITO_JWT_HEADER_PREFIX = 'Bearer'
    # config for flask_cognito_lib
    AWS_REGION = COGNITO_REGION
    AWS_COGNITO_USER_POOL_ID = COGNITO_USERPOOL_ID
    AWS_COGNITO_DOMAIN = "https://contracts.auth.eu-north-1.amazoncognito.com"
    AWS_COGNITO_USER_POOL_CLIENT_ID = COGNITO_APP_CLIENT_ID
    AWS_COGNITO_USER_POOL_CLIENT_SECRET = "1pq4nkn81klm0ssohrg53ps05tgte4h7m85o1huseqaakbo1dfbl"
    AWS_COGNITO_REDIRECT_URL = 'http://localhost:5000/postlogin'
    AWS_COGNITO_COOKIE_AGE_SECONDS = 3600
    AWS_COGNITO_LOGOUT_URL = "http://localhost:5000/postlogout"


boto_client = boto3.client('cognito-idp', Config.AWS_REGION)
app = Flask(__name__)
app.config.from_object(Config)
flask_coginto = CognitoAuth(app)
cognito_lib_auth = CognitoLibAuth(app)
# cogauth = CognitoAuth(app)
engine = create_engine('sqlite:///db.db')  # connect to server
Base.metadata.create_all(engine)
crud = CRUD(engine)

@app.route('/user', methods = ['POST'])
@cognito_auth_required
def create_user():
    # this route works with flask-cognito jwt - no session cookie available
    user_data = boto_client.admin_get_user(UserPoolId=Config.AWS_COGNITO_USER_POOL_ID,
                                           Username=current_cognito_jwt['username'])

    user_attributes = user_data["UserAttributes"]
    user_dict = {attr["Name"]: attr["Value"] for attr in user_attributes}
    user_id = current_cognito_jwt['sub']
    user = UserDto(id=user_id,
                   name=user_dict['name'],
                   email=user_dict['email'],
                   data={}
                   )
    existing_user = crud.get_user(UUID(user_id))
    res = jsonify({
        'cognito_sub': str(current_cognito_jwt['sub']),  # from cognito pool
        'jwt': str(current_cognito_jwt),  # from your database
    })
    if existing_user:
        pass
    else:
        crud.create_user(user)

    return res


@app.route("/login")
@cognito_login
def login():
    # A simple route that will redirect to the Cognito Hosted UI.
    # No logic is required as the decorator handles the redirect to the Cognito
    # hosted UI for the user to sign in.
    # An optional "state" value can be set in the current session which will
    # be passed and then used in the postlogin route (after the user has logged
    # into the Cognito hosted UI); this could be used for dynamic redirects,
    # for cookie, set `session['state'] = "some_custom_value"` before passing
    # the user to this route
    pass


@app.route('/postlogin')
@cognito_login_callback
def post_login():
    return redirect(url_for("claims"))


@app.route("/logout")
@cognito_logout
def logout():
    # Logout of the Cognito User pool and delete the cookies that were set
    # on login.
    # No logic is required here as it simply redirects to Cognito
    return


@app.route("/claims")
@auth_required()
def claims():
    raw_accessToken = request.cookies['cognito_access_token']
    raw_claims = session["claims"]
    user_name = raw_claims['username']
    user_data = boto_client.admin_get_user(UserPoolId=Config.AWS_COGNITO_USER_POOL_ID,
                                           Username=user_name)
    return jsonify({
        "claims": raw_claims,
        "user_name": user_name,
        "accessToken": raw_accessToken,
        "user_data": user_data
    })


@app.route("/postlogout")
def postlogout():
    # This is the endpoint Cognito redirects to after a user has logged out,
    # handle any logic here, like returning to the homepage.
    # This route must be set as one of the User Pool client's Sign Out URLs.
    return redirect(url_for("login"))


@app.errorhandler(AuthorisationRequiredError)
def auth_error_handler(err):
    # Register an error handler if the user hits an "@auth_required" route
    # but is not logged in to redirect them to the Cognito UI
    return redirect(url_for("login"))


@app.errorhandler(CognitoGroupRequiredError)
def missing_group_error_handler(err):
    # Register an error handler if the user hits an "@auth_required" route
    # but is not in all of groups specified
    return jsonify("Group membership does not allow access to this resource"), 403
