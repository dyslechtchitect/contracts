from db.crud import CRUD

from dto import UserDto, ContractDto


class DbAdapter:
    def __init__(self, crud: CRUD):
        self.crud = crud

    def create_user(self,
                    user_Dto: UserDto):
        user = user_Dto.as_sql_alchemy()
        return self.crud.create_user(user)

    def create_contract(self,
                        user_dto: UserDto,
                        contract_dto: ContractDto,
                        is_creator=True,
                        is_editor=True,
                        is_party=False):
        user = user_dto.as_sql_alchemy()
        contract = contract_dto.as_sql_alchemy()

        return self.crud.create_contract(user,
                                         contract,
                                         is_creator=is_creator,
                                         is_editor=is_editor,
                                         is_party=is_party)



