from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
import uuid

from custom_types.guid import UUID
from models import User, Base


engine = create_engine("sqlite://", echo=True)
Base.metadata.create_all(engine)
class CRUD:
    def __init__(self, engine, session: Session):
        self.engine = engine
        self.session = session

    def create_user(self, user: User):
        self.session.add(user)
        self.session.commit()

    def get_user(self, user_id: UUID()):
        query = select(User).where(User.id == user_id)
        return self.session.scalars(query).one()

with Session(engine) as session:
    user = User(
        id = uuid.uuid4().bytes,
        name = "ron",
        email = "ron.neuman@gmail.com",
        data = {"foo": "bar"})

    crud = CRUD(engine, session)
    crud.create_user(user)
    ret = crud.get_user(user.id)
    print(ret)
