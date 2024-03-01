from typing import List
from typing import Optional
from sqlalchemy import ForeignKey, Column
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase
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

class User(Base):
    __tablename__ = "user"
    id = Column(UUID(), primary_key=True)
    name: Mapped[Optional[str]]
    email: Mapped[Optional[str]]
    data: Mapped[dict[str, Any]]
    addresses: Mapped[List["Address"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    def __repr__(self) -> str:
        return f"User(id={self.id!r}, name={self.name!r}, fullname={self.fullname!r})"

class Address(Base):
    __tablename__ = "address"
    id: Mapped[int] = mapped_column(primary_key=True)
    email_address: Mapped[str]
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    user: Mapped["User"] = relationship(back_populates="addresses")
    def __repr__(self) -> str:
        return f"Address(id={self.id!r}, email_address={self.email_address!r})"

engine = create_engine("sqlite://", echo=True)
Base.metadata.create_all(engine)