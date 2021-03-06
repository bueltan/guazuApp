from database.model_account import ModelAccount
from database import base

session = base.Session()


def save_account(data):
    message = ModelAccount(**data)
    session.merge(message)
    session.commit()
    session.close()


def update_account(data):
    session.merge(data)
    session.commit()
    session.close()


def load_account_from_db():
    msg = session.query(ModelAccount).first()
    session.close()
    return msg


def save_image_account(id):
    pass
