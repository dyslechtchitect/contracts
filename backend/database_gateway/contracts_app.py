from typing import Optional

import uuid

from adapters.boto_adapter import BotoAdapter
from adapters.db_adapter import DbAdapter
from dto import UserDto, ContractDto


class ContractsApp:
    def __init__(self, db_adapter: DbAdapter, boto_adapter: BotoAdapter):
        self.db_adapter = db_adapter
        self.boto_adapter = boto_adapter

    def _get_user_data(self, user_id: str,
                       username: str):
        user_dict = self.boto_adapter.get_user_data(username)
        return UserDto(id=user_id,
                       name=user_dict['name'],
                       email=user_dict['email'],
                       data={})

    def create_user(self, user_id: str, username: str) -> Optional[str]:
        existing_user = self.db_adapter.get_user(user_id)
        if existing_user:
            print("already existing")
            return existing_user.id
        else:
            user_dto: UserDto = self._get_user_data(user_id, username)
            self.db_adapter.create_user(user_dto)
            return user_id

    def get_user(self, user_id: str) -> UserDto:
        return self.db_adapter.get_user(user_id)

    def create_contract(self, user_id: str, contract_data: dict) -> str:
        contract_id = str(uuid.uuid4())
        contract_dto = ContractDto(id=contract_id,
                                   **contract_data)
        self.db_adapter.create_contract(user_id, contract_dto)
        return contract_id

    def get_contract(self, user_id: str, contract_id: str) -> ContractDto:
        return self.db_adapter.get_contract(user_id, contract_id)

    def share_contract(self, user_id, email, contract_id) -> Optional[ContractDto]:
        contract_dto = self.db_adapter.share_contract(user_id, email, contract_id)
        if contract_dto:
            return contract_dto
        else:
            return

    def list_contracts(self, user_id: str) -> [str]:
        return self.db_adapter.list_contracts(user_id)