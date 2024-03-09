from botocore.client import BaseClient

from config import Config


class BotoAdapter:
    def __init__(self, boto_idp_client: BaseClient):
        self.boto_idp_client = boto_idp_client

    def get_user_data(self,
                      username: str):
        user_data = self.boto_idp_client.admin_get_user(UserPoolId=Config.AWS_COGNITO_USER_POOL_ID,
                                                        Username=username)
        user_attributes = user_data["UserAttributes"]
        return {attr["Name"]: attr["Value"] for attr in user_attributes}

