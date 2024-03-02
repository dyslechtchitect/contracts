from sqlalchemy import create_engine, select, Boolean
from sqlalchemy.orm import Session
import uuid
from datetime import datetime
from db.custom_types.guid import UUID
from db.models import User, Base, Contract, UsersToContracts

engine = create_engine('sqlite:///db.db')  # connect to server

Base.metadata.create_all(engine)
from db.crud import CRUD
with Session(engine) as session:
    user = User(
        id=uuid.uuid4().bytes,
        name="ron",
        email="ron.neuman@gmail.com",
        data={"foo": "bar"},
        date_created=datetime.now(),
        date_updated=datetime.now()
    )

    another_user = User(
        id=uuid.uuid4().bytes,
        name="bon",
        email="bon.neuman@gmail.com",
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
                        data={"contract2": ["foo"]},
                        date_created=datetime.now(),
                        date_updated=datetime.now(),
                        date_signed=datetime.now(),
                        date_expires=datetime.now()
                        )

    crud = CRUD(engine, session)
    crud.create_user(user)
    crud.create_user(another_user)

    crud.create_contract(user, contract, True, False, False)
    crud.create_contract(another_user, contract, False, False, True)

    crud.create_contract_without_user(another_contract) # checking if i can create a contract on it's own
    ret = crud.get_user(another_user.id)
    print(ret)
    contract_ids = crud.list_contracts(user.id)
    print(contract_ids)
    for c in contract_ids:
        for id in c:
            print(crud.get_contract(id))
    session.commit()