from datetime import datetime
from .db.crud import CRUD
from .db.custom_types.guid import UUID
from .db.models import User, Contract
from dataclasses import dataclass

@dataclass
class UserDto:
    id: UUID
    name: str
    email: str
    data: dict
    date_created: datetime = datetime.now()
    date_update: datetime = datetime.now()

@dataclass
class ContractDto:
    id: UUID
    data: dict
    date_created: datetime = datetime.now()
    date_update: datetime = datetime.now()
    date_created: datetime = datetime.now()
    date_update: datetime = datetime.now()
    date_signed: datetime = datetime.now()
    date_expires: datetime = datetime(year=datetime.now().year + 1)


class DbAdapter:
    def __init__(self, crud: CRUD):
        self.crud = crud

    def create_contract(self,
                        creator: UserDto,
                        contract: ContractDto,
                        sharedWith: UserDto = None):
        user = User(creator.id)
        contract = Contract(contract.id)
        self.crud.create_user(user)
        self.crud.create_contract(user, contract, is_creator=True, is_editor=True, is_party=False)


