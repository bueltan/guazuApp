from .base import Base
from sqlalchemy import Column, ForeignKey, Integer, String, Boolean
from .model_messages import ModelMessages
from sqlalchemy.orm import relationship


def node_default(context):
    return context.get_current_parameters()['phone_id']


class ModelTickets(Base):
    """Tickets model."""

    __tablename__ = 'Tickets'
    id = Column('id', Integer, primary_key=True, doc=" unique Id of the ticket.")
    idTk = Column('idTk', String(50), doc="Id of the ticket")
    idCode = Column('idCode', String(50), default=0, doc="Id of the destination phone.")
    node2 = Column('node2', String(15), default='', doc="Entity")
    node3 = Column('node3', String(15), default='', doc="area")
    node4 = Column('node4', String(15), default='', doc="account")
    phone = Column('phone', String(15), doc="Phone number of the contact_class what do some entry")
    name = Column('name', String(30), doc="name of the contact_class what do some entry")
    image = Column('image', String(200), doc="Link of the contact_class profile picture ")
    count = Column('count', Integer, default=1, doc="keep te count of activity")
    lastIdMsg = Column('lastIdMsg', String(100), doc="last message id")
    readed = Column('readed', Boolean, default = False )
    timestamp = Column('timestamp', String(20), doc="Record timestamp.")

    listMessage = relationship(ModelMessages, backref="Tickets")
