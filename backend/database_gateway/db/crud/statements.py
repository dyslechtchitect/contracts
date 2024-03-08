from sqlalchemy import select
from sqlalchemy.orm import joinedload

from db.models import User, UsersToContracts, Contract


def get_user_stmt(user_id: str):
    return select(User).where(User.id == user_id)


def get_user_by_email_stmt(user_email: str):
    return select(User).where(User.email == user_email)


def contract_already_assigned_to_user_stmt(session, contract_id: str, user_id: str):
    return (session.query(1)
            .where(UsersToContracts.user_id == user_id and UsersToContracts.user_id == user_id))


def get_contract_stmt(session, user_id: str, contract_id: str):
    return (session.query(Contract).
            join(UsersToContracts, UsersToContracts.contract_id == contract_id).
            options(joinedload(Contract.users)).
            outerjoin(User, UsersToContracts.user_id == user_id).
            filter(Contract.id == contract_id)). \
            limit(1)


def list_contracts_stmt(session, user_id: str):
    return session.query(UsersToContracts.contract_id).where(UsersToContracts.user_id == user_id)