import os

import uvicorn
from pydantic import BaseModel
from fastapi import FastAPI, Depends
from fastapi_cloudauth.cognito import Cognito, CognitoCurrentUser, CognitoClaims

app = FastAPI()
auth = Cognito(
    region="eu-north-1",
    userPoolId="eu-north-1_Ia3PeTo0f",
    client_id="4gi33ef3i1cm3s39mob5gcmn56"
)


@app.get("/", dependencies=[Depends(auth.scope(["read:users"]))])
def secure():
    # access token is valid
    return "Hello"


class AccessUser(BaseModel):
    sub: str


@app.get("/access/")
def secure_access(current_user: AccessUser = Depends(auth.claim(AccessUser))):
    # access token is valid and getting user info from access token
    return f"Hello", {current_user.sub}


get_current_user = CognitoCurrentUser(
    region="eu-north-1",
    userPoolId="eu-north-1_Ia3PeTo0f",
    client_id="4gi33ef3i1cm3s39mob5gcmn56"
)


@app.get("/user/")
def secure_user(current_user: CognitoClaims = Depends(get_current_user)):
    # ID token is valid and getting user info from ID token
    return f"Hello, {current_user.username}"

