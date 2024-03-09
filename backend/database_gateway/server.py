# configuration
import json
import uuid

from botocore.client import BaseClient
from flask import Flask, session, request, redirect, url_for
from flask_cognito import cognito_auth_required, current_cognito_jwt
from flask import jsonify
from flask_cognito import CognitoAuth
from sqlalchemy import create_engine

from adapters.boto_adapter import BotoAdapter
from adapters.db_adapter import DbAdapter
from config import Config
from contracts_app import ContractsApp
from db.models import Base
from db.crud.crud import CRUD
from dto import ContractDto
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

boto_client: BaseClient = boto3.client('cognito-idp', Config.AWS_REGION)
app = Flask(__name__)
app.config.from_object(Config)
cognito_lib_auth = CognitoLibAuth(app)
flask_coginto = CognitoAuth(app)

engine = create_engine('sqlite:///db.db')  # connect to server
Base.metadata.create_all(engine)
crud = CRUD(engine)
db_adapter = DbAdapter(crud)
boto_adapter = BotoAdapter(boto_client)
contracts_app = ContractsApp(db_adapter, boto_adapter)


@app.route('/user', methods=['POST'])
@cognito_auth_required
def create_user():
    # this route works with flask-cognito jwt - no session cookie available
    user_id = current_cognito_jwt['sub']
    username = current_cognito_jwt['username']

    return contracts_app.create_user(user_id, username)


@app.route('/user')
@cognito_auth_required
def get_user():
    user_id = current_cognito_jwt['sub']

    return contracts_app.get_user(user_id).as_json()


@app.route('/contract', methods=['POST'])
@cognito_auth_required
def create_contract():
    json_dict = request.get_json()
    user_id = current_cognito_jwt['sub']
    contract_id = contracts_app.create_contract(user_id, json_dict)
    return {'contract_id': contract_id}


@app.route('/token')
@cognito_auth_required
def get_token():
    return str(current_cognito_jwt)


@app.route('/contract/<contract_id>')
@cognito_auth_required
def get_contract(contract_id):
    user_id = current_cognito_jwt['sub']
    dto = contracts_app.get_contract(user_id, contract_id)
    return dto.as_json() if dto else None


@app.route('/contract/<contract_id>', methods=['POST'])
@cognito_auth_required
def share_contract(contract_id):
    user_id = current_cognito_jwt['sub']
    json_dict = request.get_json()
    email = json_dict["email"]
    dto = contracts_app.share_contract(user_id, email, contract_id)
    return dto.as_json() if dto else None


@app.route('/user/contracts')
@cognito_auth_required
def list_contracts():
    user_id = current_cognito_jwt['sub']
    ids = contracts_app.list_contracts(user_id)
    return json.dumps(ids)


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


if __name__ == '__main__':
    app.run(debug=True)
