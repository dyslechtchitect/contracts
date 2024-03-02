from datetime import datetime
from db.crud import CRUD

from db.models import User, Contract
from dataclasses import dataclass
import uuid
@dataclass
class UserDto:
    id: str
    name: str
    email: str
    data: dict
    date_created: datetime = datetime.now()
    date_update: datetime = datetime.now()

@dataclass
class ContractDto:
    id: str
    data: dict
    date_created: datetime = datetime.now()
    date_update: datetime = datetime.now()
    date_created: datetime = datetime.now()
    date_update: datetime = datetime.now()
    date_signed: datetime = datetime.now()
    date_expires: datetime = datetime(year=datetime.now().year + 1, month=datetime.now().month, day=datetime.now().day)


class DbAdapter:
    def __init__(self, crud: CRUD):
        self.crud = crud

    def create_contract(self,
                        creator: UserDto,
                        contract: ContractDto,
                        is_creator=True,
                        is_editor=True,
                        is_party=False):
        user = User(uuid.UUID(creator.id).bytes)
        contract = Contract(uuid.UUID(contract.id).bytes)
        self.crud.create_user(user)
        self.crud.create_contract(user,
                                  contract,
                                  is_creator=is_creator,
                                  is_editor=is_editor,
                                  is_party=is_party)
        return
    def share_contract(self,
                        share_with: UserDto,
                        contract: ContractDto,
                        is_creator=False,
                        is_editor=False,
                        is_party=True):

        return self.create_contract(share_with, contract, is_creator, is_editor, is_party)




