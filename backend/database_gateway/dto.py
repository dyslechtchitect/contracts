import uuid
from dataclasses import dataclass
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
        return User(id=uuid.UUID(self.id).bytes,
                    name=self.name,
                    email=self.email,
                    data=self.data,
                    date_created=self.date_created,
                    date_updated=self.date_updated)


@dataclass
class ContractDto:
    id: str
    data: dict
    date_created: datetime = datetime.now()
    date_updated: datetime = datetime.now()
    date_signed: datetime = datetime.now()
    date_expires: datetime = datetime(year=datetime.now().year + 1, month=datetime.now().month, day=datetime.now().day)

    def as_sql_alchemy(self):
        return Contract(id=uuid.UUID(self.id).bytes,
                        data=self.data,
                        date_created=self.date_created,
                        date_updated=self.date_updated,
                        date_signed=self.date_signed,
                        date_expires=self.date_expires)
