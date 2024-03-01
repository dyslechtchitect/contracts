from sqlalchemy import create_engine, select, Boolean
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

    def create_contract(self,
                        user: User,
                        contract: Contract,
                        is_creator: Boolean,
                        is_editor: Boolean,
                        is_party: Boolean):
        users_to_contracts = UsersToContracts(is_creator=is_creator,
                                              is_party=is_party,
                                              is_editor=is_editor)
        users_to_contracts.contract = contract
        user.contracts.append(users_to_contracts)

    def create_contract_without_user(self, contract: Contract):
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

    contract = Contract(id=uuid.uuid4().bytes,
                        data={"contract": ["foo"]},
                        date_created=datetime.now(),
                        date_updated=datetime.now(),
                        date_signed=datetime.now(),
                        date_expires=datetime.now()
                        )
    another_contract = Contract(id=uuid.uuid4().bytes,
                        data={"contract": ["foo"]},
                        date_created=datetime.now(),
                        date_updated=datetime.now(),
                        date_signed=datetime.now(),
                        date_expires=datetime.now()
                        )

    crud = CRUD(engine, session)
    crud.create_user(user)

    crud.create_contract(user, contract, True, False, False)
    ret = crud.get_user(user.id)
    print(ret)
    crud.create_contract_without_user(another_contract) # checking if i can create a contract on it's own
