from sqlalchemy import select, Boolean
from sqlalchemy.orm import Session

from custom_types.guid import UUID
from models import User, Contract, UsersToContracts


class CRUD:
    def __init__(self, engine, session: Session):
        self.engine = engine
        self.session = session

    def create_user(self, user: User):
        self.session.add(user)



    def get_user(self, user_id: UUID()):
        query = select(User).where(User.id == user_id)
        return self.session.scalars(query).one()

    def create_contract(self,
                        user: User,
                        contract: Contract,
                        is_creator: Boolean,
                        is_editor: Boolean,
                        is_party: Boolean):
        users_to_contracts = UsersToContracts(is_creator=is_creator,
                                              is_party=is_party,
                                              is_editor=is_editor)
        users_to_contracts.contract = contract
        user.contracts.append(users_to_contracts)
        print("what?")

    def list_contracts(self, user_id: UUID()):
        return self.session.query(Contract.id)\
        .join(UsersToContracts, UsersToContracts.user_id == user_id)\
        .all()
    def get_contract(self, contract_id: UUID()):
        query = select(Contract).where(Contract.id == contract_id)
        return self.session.scalars(query).one()


    def create_contract_without_user(self, contract: Contract):
        self.session.add(contract)


