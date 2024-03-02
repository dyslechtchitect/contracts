import json
from typing import List
from typing import Optional
from sqlalchemy import ForeignKey, Column, Table, Boolean
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from db.custom_types.guid import UUID
from typing import Any
from datetime import datetime
from sqlalchemy.types import JSON
from sqlalchemy_serializer import SerializerMixin


class Base(DeclarativeBase, SerializerMixin):
    type_annotation_map = {
        dict[str, Any]: JSON
    }


class UsersToContracts(Base):
    __tablename__ = 'users_to_contracts'

    user_id: Mapped[UUID] = mapped_column(ForeignKey('user.id'), primary_key=True)
    contract_id: Mapped[UUID] = mapped_column(ForeignKey('contract.id'), primary_key=True)
    is_creator = Column(Boolean)
    is_editor = Column(Boolean)
    is_party = Column(Boolean)
    user: Mapped["User"] = relationship(back_populates="contracts")
    contract: Mapped["Contract"] = relationship(back_populates="users")


class User(Base):
    __tablename__ = "user"
    id = Column(UUID, primary_key=True)
    name: Mapped[Optional[str]]
    email: Mapped[Optional[str]]
    data: Mapped[dict[str, Any]]
    contracts: Mapped[List["UsersToContracts"]] = relationship(
        back_populates="user"
    )
    date_created: Mapped[datetime]
    date_updated: Mapped[datetime]

    def __repr__(self) -> str:
        return json.dumps({
            "id": str(self.id),
            "name": self.name,
            "email": self.email,
            "data": self.data,
            "date_created": str(self.date_created),
            "date_updated": str(self.date_updated)
        }
        )


class Contract(Base):
    __tablename__ = "contract"
    id = Column(UUID, primary_key=True)
    data: Mapped[dict[str, Any]]
    users: Mapped[List["UsersToContracts"]] = relationship(
        back_populates="contract"
    )

    date_created: Mapped[datetime]
    date_updated: Mapped[datetime]
    date_signed: Mapped[datetime]
    date_expires: Mapped[datetime]

    def __repr__(self) -> str:
        return json.dumps({
            "id": str(self.id),
            "data": self.data,
            "date_created": str(self.date_created),
            "date_updated": str(self.date_updated),
            "date_signed": str(self.date_signed),
            "date_expires": str(self.date_expires)
        }
        )
