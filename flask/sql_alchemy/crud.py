from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
import uuid
from datetime import datetime
from custom_types.guid import UUID
from models import User, Base, Contract, UsersToContracts

engine = create_engine('sqlite:///db.db')  # connect to server

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

    def create_contract(self, contract: Contract):
        self.session.add(contract)
        self.session.commit()


with Session(engine) as session:
    user = User(
        id=uuid.uuid4().bytes,
        name="ron",
        email="ron.neuman@gmail.com",
        data={"foo": "bar"},
        date_created=datetime.now(),
        date_updated=datetime.now()
    )
    users_to_contracts = UsersToContracts(is_creator=True, is_party=False, is_editor=False)
    contract = Contract(id=uuid.uuid4().bytes,
                        data={"contract": ["foo"]},
                        date_created=datetime.now(),
                        date_updated=datetime.now(),
                        date_signed=datetime.now(),
                        date_expires=datetime.now()
                        )

    crud = CRUD(engine, session)
    crud.create_user(user)
    # crud.create_contract(contract)
    users_to_contracts.contract = contract
    user.contracts.append(users_to_contracts)
    session.commit()
    ret = crud.get_user(user.id)
    print(ret)
