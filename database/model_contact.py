from .base import Base
from sqlalchemy import Column, String, Integer, ForeignKey, Boolean


class ModelContact(Base):
    """Contact model."""
    __tablename__ = 'Contact'
    id = Column('id', String(40), primary_key=True, doc="Id of the contact ")
    id_account = Column('id_account', ForeignKey('Account.id'), doc="Id of the account")
    id_name_contact = Column('id_name_contact', String(50), doc="")
    name_contact = Column('name_contact', String(30))
    type_contact = Column('type_contact', String(10))
    image_contact = Column('image_contact', String(200))
    id_ticket = Column('id_ticket', ForeignKey('Tickets.id'), doc="Id of the tks")
    phone = Column('phone', String(15), nullable=False, doc="phone number.")
