from sqlalchemy import create_engine

import uuid

from models import User, Base
from sqlalchemy.orm import Session

engine = create_engine("sqlite://", echo=True)
Base.metadata.create_all(engine)
class CRUD:
    def __init__(self, engine):
        self.engine = engine

    def create_user(self, user: User):
        with Session(self.engine) as session:
            print(user)
            session.add(user)
            session.commit()

user = User(id = uuid.uuid4().bytes,
    name = "ron",
    email = "ron.neuman@gmail.com",
    data = {"foo": "bar"})

ret = CRUD(engine).create_user(user)
