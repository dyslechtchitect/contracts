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


class UsersToContracts(Base):
    __tablename__ = 'users_to_contracts'

    user_id: Mapped[UUID()] = mapped_column(ForeignKey('user.id'), primary_key=True)
    contract_id: Mapped[UUID()] = mapped_column(ForeignKey('contract.id'), primary_key=True)
    is_creator = Column(Boolean)
    is_editor = Column(Boolean)
    is_party = Column(Boolean)
    user: Mapped["User"] = relationship(back_populates="contracts")
    contract: Mapped["Contract"] = relationship(back_populates="users")

class User(Base):
    __tablename__ = "user"
    id = Column(UUID(), primary_key=True)
    name: Mapped[Optional[str]]
    email: Mapped[Optional[str]]
    data: Mapped[dict[str, Any]]
    contracts: Mapped[List["UsersToContracts"]] = relationship(
        back_populates="user"
    )
    date_created: Mapped[datetime]
    date_updated: Mapped[datetime]
    def __repr__(self) -> str:
        return f"""{self.id}"""

class Contract(Base):
    __tablename__ = "contract"
    id = Column(UUID(), primary_key=True)
    data: Mapped[dict[str, Any]]
    users: Mapped[List["UsersToContracts"]] = relationship(
        back_populates="contract"
    )

    date_created: Mapped[datetime]
    date_updated: Mapped[datetime]
    date_signed: Mapped[datetime]
    date_expires: Mapped[datetime]
    def __repr__(self) -> str:
        return f"""{self.id}"""

