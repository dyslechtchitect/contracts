# configuration
import json

from flask import Flask, session, request, redirect, url_for, Response
from flask import jsonify
from flask_cognito import cognito_auth_required, current_cognito_jwt
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

from contracts_app import ContractsApp


class ContractsServer:

    def __init__(self,
                 app: Flask,
                 contracts_app: ContractsApp
                 ):
        self.app = app
        self._contracts_app = contracts_app
        self._init_rules()
        self._init_error_handlers()

    def _init_rules(self):
        self.app.add_url_rule('/user', 'get_user', self.get_user, methods=['GET'])
        self.app.add_url_rule('/user', 'create_user', self.create_user, methods=['POST'])
        self.app.add_url_rule('/contract', 'create_contract', self.create_contract, methods=['POST'])
        self.app.add_url_rule('/contract/<contract_id>', 'get_contract', self.get_contract, methods=['GET'])
        self.app.add_url_rule('/contract/<contract_id>', 'share_contract', self.share_contract, methods=['POST'])
        self.app.add_url_rule('/user/contracts', 'list_contract', self.list_contracts, methods=['GET'])
        self.app.add_url_rule('/token', 'token', self.get_token, methods=['GET'])
        self.app.add_url_rule('/login', 'login', self.login, methods=['GET'])
        self.app.add_url_rule('/postlogin', 'post_login', self.post_login, methods=['GET'])
        self.app.add_url_rule('/logout', 'logout', self.logout, methods=['GET'])
        self.app.add_url_rule('/claims', 'claims', self.claims, methods=['GET'])
        self.app.add_url_rule('/postlogout', 'post_logout', self.postlogout, methods=['GET'])

    def _init_error_handlers(self):
        self.app.register_error_handler(AuthorisationRequiredError, self.auth_error_handler)
        self.app.register_error_handler(CognitoGroupRequiredError, self.missing_group_error_handler)

    @cognito_auth_required
    def create_user(self):

        print('was here')
        # this route works with flask-cognito jwt - no session cookie available
        user_id = current_cognito_jwt['sub']
        username = current_cognito_jwt['username']

        return self._contracts_app.create_user(user_id, username)

    @cognito_auth_required
    def get_user(self):
        user_id = current_cognito_jwt['sub']

        return self._contracts_app.get_user(user_id).as_json()

    @cognito_auth_required
    def create_contract(self):
        json_dict = request.get_json()
        user_id = current_cognito_jwt['sub']
        contract_id = self._contracts_app.create_contract(user_id, json_dict)

        return Response(json.dumps({'contract_id': contract_id}), status=201, mimetype='application/json')

    @cognito_auth_required
    def get_token(self):
        return str(current_cognito_jwt)

    @cognito_auth_required
    def get_contract(self, contract_id):
        user_id = current_cognito_jwt['sub']
        dto = self._contracts_app.get_contract(user_id, contract_id)
        body = dto.as_json() if dto else None

        return  Response(body, status=200, mimetype='application/json')

    @cognito_auth_required
    def share_contract(self, contract_id):
        user_id = current_cognito_jwt['sub']
        json_dict = request.get_json()
        email = json_dict["email"]
        dto = self._contracts_app.share_contract(user_id, email, contract_id)
        return dto.as_json() if dto else None


    @cognito_auth_required
    def list_contracts(self):
        user_id = current_cognito_jwt['sub']
        ids = self._contracts_app.list_contracts(user_id)
        return json.dumps(ids)

    @cognito_login
    def login(self):
        # A simple route that will redirect to the Cognito Hosted UI.
        # No logic is required as the decorator handles the redirect to the Cognito
        # hosted UI for the user to sign in.
        # An optional "state" value can be set in the current session which will
        # be passed and then used in the postlogin route (after the user has logged
        # into the Cognito hosted UI); this could be used for dynamic redirects,
        # for cookie, set `session['state'] = "some_custom_value"` before passing
        # the user to this route
        pass




    @cognito_login_callback
    def post_login(self):
        return redirect(url_for("claims"))


    @cognito_logout
    def logout(self):
        # Logout of the Cognito User pool and delete the cookies that were set
        # on login.
        # No logic is required here as it simply redirects to Cognito
        return


    @auth_required()
    def claims(self):
        raw_accessToken = request.cookies['cognito_access_token']
        raw_claims = session["claims"]
        user_name = raw_claims['username']
        user_data = self._contracts_app.get_user_data( user_name)
        return jsonify({
            "claims": raw_claims,
            "user_name": user_name,
            "accessToken": raw_accessToken,
            "user_data": user_data
        })


    def postlogout(self):
        # This is the endpoint Cognito redirects to after a user has logged out,
        # handle any logic here, like returning to the homepage.
        # This route must be set as one of the User Pool client's Sign Out URLs.
        return redirect(url_for("login"))


    def auth_error_handler(self, err):
        # Register an error handler if the user hits an "@auth_required" route
        # but is not logged in to redirect them to the Cognito UI
        return redirect(url_for("login"))


    def missing_group_error_handler(self, err):
        # Register an error handler if the user hits an "@auth_required" route
        # but is not in all of groups specified
        return jsonify("Group membership does not allow access to this resource"), 403


