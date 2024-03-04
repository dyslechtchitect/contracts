from os import environ, urandom


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
