from .base import Base
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .model_tickets import ModelTickets


class ModelSubscriptions(Base):
    """Subscriptions model."""

    __tablename__ = 'Subscriptions'
    id = Column('id', String(40), primary_key=True, doc="Id of the subscriptions ")
    id_account = Column('id_account', ForeignKey('Account.id', ondelete='CASCADE'), doc="Id of the account")
    code = Column('code', String(4), doc="code")
    source = Column('source', String(100), nullable=False, doc="from where is subscrited .")
    last_sync_timestamp = Column('last_sync_timestamp', Integer, default=0, doc="last timestamp sync subscriptions")