from typing import List
from typing import Optional
from sqlalchemy import ForeignKey, Column,Table, Boolean
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import BINARY
from sqlalchemy.types import TypeDecorator
from custom_types.guid import UUID
from typing import Any
from datetime import datetime
from flask import jsonify
from sqlalchemy.types import JSON
from sqlalchemy import create_engine
from sqlalchemy_serializer import SerializerMixin
import json

class Base(DeclarativeBase, SerializerMixin):
    type_annotation_map = {
        dict[str, Any]: JSON
    }


users_to_contracts = Table(
    'users_to_contracts',
    Base.metadata,
    Column('user_id', UUID(), ForeignKey('user.id'), primary_key=True),
    Column('contract_id', UUID(), ForeignKey('contract.id'), primary_key=True),
    Column('is_creator', Boolean),
    Column('is_editor', Boolean),
    Column('is_party', Boolean)
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
    date_created: Mapped[datetime]
    date_updated: Mapped[datetime]
    def __repr__(self) -> str:
        return f"""{self.id}"""

class Contract(Base):
    __tablename__ = "contract"
    id = Column(UUID(), primary_key=True)
    data: Mapped[dict[str, Any]]
    users: Mapped[List["User"]] = relationship(
        back_populates="contracts",
        secondary=users_to_contracts
    )

    date_created: Mapped[datetime]
    date_updated: Mapped[datetime]
    date_signed: Mapped[datetime]
    date_expires: Mapped[datetime]
    def __repr__(self) -> str:
        return f"""{self.id}"""

