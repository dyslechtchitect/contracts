# configuration

import boto3
from botocore.client import BaseClient
from flask import Flask
from flask_cognito import CognitoAuth
from flask_cognito_lib import CognitoAuth as CognitoLibAuth
from sqlalchemy import create_engine

from adapters.boto_adapter import BotoAdapter
from adapters.db_adapter import DbAdapter
from config import Config
from contracts_app import ContractsApp
from db.crud.crud import CRUD
from db.models import Base
from server import ContractsServer


class Boiler:
    boto_client: BaseClient = boto3.client('cognito-idp', Config.AWS_REGION)
    app: Flask = Flask(__name__)
    app.config.from_object(Config)
    with app.app_context():
        cognito_lib_auth = CognitoLibAuth(app)
        flask_coginto = CognitoAuth(app)

        engine = create_engine(f'sqlite:///{Config.DB_NAME}.db')  # connect to server
        Base.metadata.create_all(engine)
        crud = CRUD(engine)
        db_adapter = DbAdapter(crud)
        boto_adapter = BotoAdapter(boto_client)
        contracts_app = ContractsApp(db_adapter, boto_adapter)
        server = ContractsServer(app, contracts_app)


if __name__ == '__main__':
    Boiler.app.run()


def create_app():
    return Boiler.app
