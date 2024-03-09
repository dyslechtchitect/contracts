from typing import Optional

from sqlalchemy import Boolean
from sqlalchemy.orm import Session

from db.crud.statements import get_user_stmt, get_user_by_email_stmt, contract_already_assigned_to_user_stmt, \
    get_contract_stmt, list_contracts_stmt
from db.models import User, Contract, UsersToContracts
from dto import UserDto, ContractDto


class CRUD:
    def __init__(self, engine):
        self.engine = engine

    def create_user(self, user_dto: UserDto):
        with Session(self.engine) as session:
            user = user_dto.as_sql_alchemy()
            session.add(user)
            session.commit()

    def get_user(self, user_id: str) -> UserDto:
        result: User
        with Session(self.engine) as session:
            stmt = get_user_stmt(user_id)
            result = self._one_or_none(session, stmt)
        return UserDto.from_sql_alchemy(result)

    def create_contract(self,
                        user_id: str,
                        contract_dto: ContractDto,
                        is_creator: Boolean,
                        is_editor: Boolean,
                        is_party: Boolean):
        with Session(self.engine) as session:
            user_stmt = get_user_stmt(user_id)
            user = self._one_or_none(session, user_stmt)
            users_to_contracts = UsersToContracts(is_creator=is_creator,
                                                  is_party=is_party,
                                                  is_editor=is_editor,
                                                  is_signed=False,
                                                  date_signed=None)

            users_to_contracts.contract = contract_dto.as_sql_alchemy()
            user.contracts.append(users_to_contracts)
            session.commit()

    def share_contract_by_email(self,
                                owner_id: str,
                                guest_email: str,
                                contract_id: str):
        shared_contract_dto: ContractDto
        existing_contract = self.get_contract(owner_id, contract_id)
        with Session(self.engine) as session:
            guest_user_stmt = get_user_by_email_stmt(guest_email)
            guest_user = self._one_or_none(session, guest_user_stmt)
            if contract_already_assigned_to_user_stmt(session, contract_id, guest_user.id):
                return existing_contract
            users_to_contracts = UsersToContracts(
                user_id=guest_user.id,
                contract_id=contract_id,
                is_creator=False,
                is_party=False,
                is_editor=False,
                is_signed=False,
                date_signed=None)
            session.add(users_to_contracts)
            shared_contract_stmt = get_contract_stmt(session, owner_id, contract_id)
            shared_contract: Contract = self._one_or_none(session, shared_contract_stmt)
            shared_contract_dto = ContractDto.from_sql_alchemy(shared_contract)
            session.commit()

        return shared_contract_dto

    def list_contracts(self, user_id: str):
        contract_ids: list[str]
        with Session(self.engine) as session:
            query = list_contracts_stmt(session, user_id)
            contracts = query.all()
            contract_ids = [row.contract_id for row in contracts]
            session.commit()
        return contract_ids

    def get_contract(self, user_id: str, contract_id: str) -> Optional[ContractDto]:
        contract_dto: ContractDto
        with Session(self.engine) as session:
            stmt = get_contract_stmt(session, user_id, contract_id)
            contract = self._one_or_none(session, stmt)
            contract_dto = ContractDto.from_sql_alchemy(contract)
            session.commit()
        return contract_dto

    def create_contract_without_user(self, contract: Contract):
        with Session(self.engine) as session:
            session.add(contract)
            session.commit()

    def _one_or_none(self, session, stmt):
        return session.scalars(stmt).one_or_none()
