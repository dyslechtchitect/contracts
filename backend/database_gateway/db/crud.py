import uuid

from sqlalchemy import select, Boolean, func
from sqlalchemy.orm import Session
from db.models import User, Contract, UsersToContracts
from dto import UserDto, ContractDto


class CRUD:
    def __init__(self, engine):
        self.engine = engine

    def create_user(self, user_dto: UserDto):
        with Session(self.engine) as session:
            print(f"creating {user_dto}")
            ret = session.add(user_dto.as_sql_alchemy())
            session.commit()
            return ret

    def get_user(self, user_id: str) -> User:
        result: User

        with Session(self.engine) as session:
            query = select(User).where(User.id == user_id)
            print(f"fetching {str(user_id)}")
            result = session.scalars(query).one_or_none()
        return result


    def create_contract(self,
                        user_dto: UserDto,
                        contract_dto: ContractDto,
                        is_creator: Boolean,
                        is_editor: Boolean,
                        is_party: Boolean):
        with Session(self.engine) as session:
            user = user_dto.as_sql_alchemy()
            users_to_contracts = UsersToContracts(is_creator=is_creator,
                                                  is_party=is_party,
                                                  is_editor=is_editor)

            users_to_contracts.contract = contract_dto.as_sql_alchemy()
            session.add(contract_dto.as_sql_alchemy())
            user.contracts.append(users_to_contracts)
            session.commit()


    def list_contracts(self, user_id: str):
        with Session(self.engine) as session:
            return session.query(Contract.id) \
                .join(UsersToContracts, UsersToContracts.user_id == user_id) \
                .all()

    def get_contract(self, contract_id: str):
        with Session(self.engine) as session:
            query = select(Contract).where(Contract.id == contract_id)
            return session.scalars(query).one()

    def create_contract_without_user(self, contract: Contract):
        with Session(self.engine) as session:
            session.add(contract)
