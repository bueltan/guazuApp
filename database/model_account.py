from .base import Base
from sqlalchemy import Column, Boolean, String


class ModelAccount(Base):
    """Account model."""

    __tablename__ = 'Account'
    id = Column('id', String(40), primary_key=True, doc="Id of the account name ")
    idName = Column('id_name', String(15), unique=True, doc="Id_name of the account ")
    name = Column('name', String(30), nullable=True, doc="Name of the person.")
    password = Column('password', String(16), nullable=False, doc="Password of the account.")
    email = Column('email', String(40), doc="Email of the account.")
    avatar = Column('avatar', String(40), doc="dir of image avatar")
    keepOpen = Column('keepOpen', Boolean, default=False, doc="get in without write user and password")
