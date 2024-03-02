from .db.crud import CRUD

class DbAdapter:
    def __init__(self, crud: CRUD):
        self.crud = crud

    def create_contract(self,
                        creator: UserDto,
                        sharedWith: UserDto,
                        contract: ContractDto):



