from os import environ, path, urandom
import jwt
from dotenv import load_dotenv
from flask import Flask, jsonify, redirect, session, url_for, request

from flask_cognito_lib import CognitoAuth
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

# Load variables from .env
basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, ".env"))


class Config:
    """Set Flask configuration vars from .env file."""

    # General Config
    SECRET_KEY = environ.get("SECRET_KEY", urandom(32))
    FLASK_APP = "TEST_APP"
    FLASK_ENV = "TESTING"

    # Cognito config
    # AWS_COGNITO_DISABLED = True  # Can set to turn off auth (e.g. for local testing)
    AWS_REGION = "eu-north-1"
    AWS_COGNITO_USER_POOL_ID = "eu-north-1_hJFEKpJQs"
    AWS_COGNITO_DOMAIN = "https://local-contracts.auth.eu-north-1.amazoncognito.com"
    AWS_COGNITO_USER_POOL_CLIENT_ID = "58ddlbqvo4ck1eks5t44rnhk0a"
    AWS_COGNITO_USER_POOL_CLIENT_SECRET = "lonop6u23g56s7phffhlnvngl0ed3ouknj1l48c4fsofkqnq83r"
    AWS_COGNITO_REDIRECT_URL = "http://localhost:5000/postlogin"
    AWS_COGNITO_COOKIE_AGE_SECONDS = 3600
    AWS_COGNITO_LOGOUT_URL = "http://localhost:5000/postlogout"


app = Flask(__name__)
app.config.from_object(Config)
auth = CognitoAuth(app)


@app.route("/")
def home():
    return "Hello world!"


@app.route("/login")
@cognito_login
def login():
    # A simple route that will redirect to the Cognito Hosted UI.
    # No logic is required as the decorator handles the redirect to the Cognito
    # hosted UI for the user to sign in.
    # An optional "state" value can be set in the current session which will
    # be passed and then used in the postlogin route (after the user has logged
    # into the Cognito hosted UI); this could be used for dynamic redirects,
    # for example, set `session['state'] = "some_custom_value"` before passing
    # the user to this route
    pass


@app.route("/postlogin")
@cognito_login_callback
def postlogin():
    # A route to handle the redirect after a user has logged in with Cognito.
    # This route must be set as one of the User Pool client's Callback URLs in
    # the Cognito console and also as the config value AWS_COGNITO_REDIRECT_URL.
    # The decorator will store the validated access token in a HTTP only cookie
    # and the user claims and info are stored in the Flask session:
    # session["claims"] and session["user_info"].
    # Do anything after the user has logged in here, e.g. a redirect or perform
    # logic based on a custom `session['state']` value if that was set before
    # login
    # print("xxx")
    # print(request.cookies['x-access-token'])
    return redirect(url_for("claims"))


@app.route("/claims")
@auth_required()
def claims():
    # This route is protected by Cognito authorisation. If the user is not
    # logged in at this point or their token from Cognito is no longer valid
    # a 401 Authentication Error is thrown, which is caught by the
    # `auth_error_handler` a redirected to the Hosted UI to login.
    # If their auth is valid, the current session will be shown including
    # their claims and user_info extracted from the Cognito tokens.
    # print("lll")
    print(session)
    print("XXX")
    accessToken = request.cookies['cognito_access_token']
    print(accessToken)
    decodedAccessToken = jwt.decode(accessToken, algorithms=["HS256"], options={"verify_signature": False})
    print("YYY")
    print(decodedAccessToken)
    # return jsonify(session.)
    return jsonify({"claims": session["claims"]})


@app.errorhandler(AuthorisationRequiredError)
def auth_error_handler(err):
    # Register an error handler if the user hits an "@auth_required" route
    # but is not logged in to redirect them to the Cognito UI
    return redirect(url_for("login"))


@app.route("/admin")
@auth_required(groups=["admin"])
def admin():
    # This route will only be accessible to a user who is a member of all of
    # groups specified in the "groups" argument on the auth_required decorator
    # If they are not, a CognitoGroupRequiredError is raised which is handled
    # by the `missing_group_error_handler` below.
    # If their auth is valid, the set of groups the user is a member of will be
    # shown.

    # Could also use: jsonify(session["user_info"]["cognito:groups"])
    return jsonify(session["claims"]["cognito:groups"])


@app.route("/edit")
@auth_required(groups=["admin", "editor"], any_group=True)
def edit():
    # This route will only be accessible to a user who is a member of any of
    # groups specified in the "groups" argument on the auth_required decorator
    # If they are not, a CognitoGroupRequiredError is raised which is handled
    # below
    return jsonify(session["claims"]["cognito:groups"])


@app.errorhandler(CognitoGroupRequiredError)
def missing_group_error_handler(err):
    # Register an error handler if the user hits an "@auth_required" route
    # but is not in all of groups specified
    return jsonify("Group membership does not allow access to this resource"), 403


@app.route("/logout")
@cognito_logout
def logout():
    # Logout of the Cognito User pool and delete the cookies that were set
    # on login.
    # No logic is required here as it simply redirects to Cognito
    pass


@app.route("/postlogout")
def postlogout():
    # This is the endpoint Cognito redirects to after a user has logged out,
    # handle any logic here, like returning to the homepage.
    # This route must be set as one of the User Pool client's Sign Out URLs.
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True, port=5000)
