from typing import List
from typing import Optional
from sqlalchemy import ForeignKey, Column,Table
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import BINARY
from sqlalchemy.types import TypeDecorator
from custom_types.guid import UUID
from typing import Any

from sqlalchemy.types import JSON
from sqlalchemy import create_engine

class Base(DeclarativeBase):
    type_annotation_map = {
        dict[str, Any]: JSON
    }

users_to_contracts = Table(
    'users_to_contracts',
    Base.metadata,
    Column('user_id', UUID(), ForeignKey('user.id'), primary_key=True),
    Column('contract_id', UUID(), ForeignKey('contract.id'), primary_key=True),
)

class User(Base):
    __tablename__ = "user"
    id = Column(UUID(), primary_key=True)
    name: Mapped[Optional[str]]
    email: Mapped[Optional[str]]
    data: Mapped[dict[str, Any]]
    contracts: Mapped[List["Contract"]] = relationship(
        back_populates="users",
        secondary=users_to_contracts
    )
    def __repr__(self) -> str:
        return f"User(id={self.id!r}, name={self.name!r}, email={self.email!r}, data={self.data})"

class Contract(Base):
    __tablename__ = "contract"
    id = Column(UUID(), primary_key=True)
    data: Mapped[dict[str, Any]]
    users: Mapped[List["User"]] = relationship(
        back_populates="contracts",
        secondary=users_to_contracts
    )
    def __repr__(self) -> str:
        return f"Contract(id={self.id!r}, data={self.data!r})"

