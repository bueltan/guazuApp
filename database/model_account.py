from .base import Base
from sqlalchemy import Column, Boolean, String,Integer


class ModelAccount(Base):
    """Account model."""

    __tablename__ = 'Account'
    id = Column('id', String(40), primary_key=True, doc="Id of the account name ")
    id_name = Column('id_name', String(15), unique=True, doc="Id_name of the account ")
    name = Column('name', String(30), nullable=True, doc="Name of the person.")
    password = Column('password', String(100), nullable=False, doc="Password of the account.")
    email = Column('email', String(60), doc="Email of the account.")
    profile_img = Column('profile_img', String(50), doc="dir of image profile")
    keepOpen = Column('keepOpen', Boolean, default=False, doc="log in without write user and password")
    current = Column('current', Boolean, default = True, doc=" if the current account")

