from db.crud import CRUD

from dto import UserDto, ContractDto


class DbAdapter:
    def __init__(self, crud: CRUD):
        self.crud = crud

    def create_user(self,
                    user_Dto: UserDto):
        return self.crud.create_user(user_Dto)

    def get_user(self, user_id: str):
        user = self.crud.get_user(user_id)
        return UserDto.from_sql_alchemy(user)

    def create_contract(self,
                        user_id: str,
                        contract_dto: ContractDto,
                        is_creator=True,
                        is_editor=True,
                        is_party=False):


        return self.crud.create_contract(user_id,
                                         contract_dto,
                                         is_creator=is_creator,
                                         is_editor=is_editor,
                                         is_party=is_party)

    def get_contract(self, user_id: str, contract_id: str) -> ContractDto:
        return self.crud.get_contract(user_id, contract_id)

    def list_contracts(self, user_id: str) -> list[ContractDto]:
        return self.crud.list_contracts(user_id)



