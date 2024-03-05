from sqlalchemy import select, Boolean
from sqlalchemy.orm import Session
from db.models import User, Contract, UsersToContracts
from dto import UserDto, ContractDto


class CRUD:
    def __init__(self, engine):
        self.engine = engine

    def create_user(self, user_dto: UserDto):
        with Session(self.engine) as session:
            self._create_user(session, user_dto)
            session.commit()

    def _create_user(self, session, user_dto: UserDto):
        return session.add(user_dto.as_sql_alchemy())

    def get_user(self, user_id: str) -> User:
        result = None
        with Session(self.engine) as session:
            stmt = self._get_user_stmt(user_id)
            result = self._one_or_none(session, stmt)
        return result

    def _get_user_stmt(self, user_id: str):
        return select(User).where(User.id == user_id)

    def create_contract(self,
                        user_id: str,
                        contract_dto: ContractDto,
                        is_creator: Boolean,
                        is_editor: Boolean,
                        is_party: Boolean):

        with Session(self.engine) as session:
            user_stmt = self._get_user_stmt(user_id)
            user = self._one_or_none(session, user_stmt)
            users_to_contracts = UsersToContracts(is_creator=is_creator,
                                                  is_party=is_party,
                                                  is_editor=is_editor)

            users_to_contracts.contract = contract_dto.as_sql_alchemy()
            user.contracts.append(users_to_contracts)
            session.commit()

    def list_contracts(self, user_id: str):
        contract_dtos: list[ContractDto]
        with Session(self.engine) as session:
            query = self._list_contracts_stmt(session, user_id)
            contracts = query.all()
            contract_dtos = [ContractDto.from_sql_alchemy(contract) for contract in contracts]
            session.commit()
        return contract_dtos

    def _list_contracts_stmt(self, session, user_id: str):
        return session.query(Contract.id).join(UsersToContracts, UsersToContracts.user_id == user_id)

    def get_contract(self, contract_id: str) -> ContractDto:
        contract_dto: ContractDto
        with Session(self.engine) as session:
            stmt = self._get_contract_stmt(contract_id)
            contract = self._one_or_none(session, stmt)
            contract_dto = ContractDto.from_sql_alchemy(contract)

        return contract_dto

    def _get_contract_stmt(self, contract_id: str):
        return select(Contract).where(Contract.id == contract_id)

    def create_contract_without_user(self, contract: Contract):
        with Session(self.engine) as session:
            session.add(contract)
            session.commit()



    def _one_or_none(self, session, stmt):
        return session.scalars(stmt)._one_or_none()