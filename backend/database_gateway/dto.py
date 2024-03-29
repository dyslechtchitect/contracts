import json
from dataclasses import dataclass, asdict
from datetime import datetime

from db.models import User, Contract


@dataclass
class UserDto:
    id: str
    name: str
    email: str
    data: dict
    date_created: datetime = datetime.now()
    date_updated: datetime = datetime.now()

    def as_sql_alchemy(self):
        return User(id=self.id,
                    name=self.name,
                    email=self.email,
                    data=self.data,
                    date_created=self.date_created,
                    date_updated=self.date_updated)

    @staticmethod
    def from_sql_alchemy(user: User):
        if user:
            return UserDto(id=user.id,
                           name=user.name,
                           email=user.email,
                           data=user.data,
                           date_created=user.date_created,
                           date_updated=user.date_updated)

    def as_json(self):
        return json.dumps({
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'data': self.data,
            'date_created': str(self.date_created),
            'date_updated': str(self.date_updated),
        })

@dataclass
class ContractRelationshipDto:
    user_id: str
    is_creator: bool
    is_editor: bool
    is_party: bool
    is_signed: bool
    date_signed: datetime

    @staticmethod
    def empty():
        return ContractRelationshipDto(None, False, False, False, False, None)
@dataclass
class ContractDto:
    id: str
    data: dict
    date_created: datetime = datetime.now()
    date_updated: datetime = datetime.now()
    date_signed: datetime = datetime.now()
    date_expires: datetime = datetime(year=datetime.now().year + 1, month=datetime.now().month, day=datetime.now().day)
    relationships: list[ContractRelationshipDto] = ContractRelationshipDto.empty()
    def as_sql_alchemy(self):
        return Contract(id=self.id,
                        data=self.data,
                        date_created=self.date_created,
                        date_updated=self.date_updated,
                        date_signed=self.date_signed,
                        date_expires=self.date_expires)

    @staticmethod
    def from_sql_alchemy(contract: Contract):
        if contract:
            return ContractDto(id=contract.id,
                               data=contract.data,
                               date_created=contract.date_created,
                               date_updated=contract.date_updated,
                               date_signed=contract.date_signed,
                               date_expires=contract.date_expires,
                               relationships=[asdict(ContractRelationshipDto(user_id=u.user_id,
                                                                             is_creator=u.is_creator,
                                                                             is_editor=u.is_editor,
                                                                             is_party=u.is_party,
                                                                             is_signed=u.is_signed,
                                                                             date_signed=str(u.date_signed))) for u in contract.users])

    def as_json(self):
        return json.dumps({
            'id': self.id,
            'data': self.data,
            'date_created': str(self.date_created),
            'date_updated': str(self.date_updated),
            'date_signed': str(self.date_signed),
            'date_expires': str(self.date_expires),
            'relationships': self.relationships
        })
