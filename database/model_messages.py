from .base import Base
from sqlalchemy import Column, String, Integer, ForeignKey, Boolean


class ModelMessages(Base):
    """Messages model."""

    __tablename__ = 'Messages'
    id = Column('id', String(80), primary_key=True, doc="Id of the MessageSent.")
    ticketsId = Column('ticketsId', ForeignKey('Tickets.id'), doc="Id of the tickets")
    type = Column('type', String(15), nullable=False, doc="Type of the message.")
    text = Column('text', String(6000), doc="Text of the massage max len 6000")
    fromMe = Column('fromMe', Boolean, doc="is the message from me.")
    mime = Column('mime', String(50), doc="format of the media data")
    url = Column('url', String(200), doc="url of file")
    caption = Column('caption', String(200), doc="caption of the message")
    filename = Column('filename', String(150), doc="name of the file ")
    payload = Column('payload', String(100), doc="Latitude and longitude")
    vcardList = Column('vcardList', String(1000), doc="List of the vcard")
    timestamp = Column('timestamp', Integer, doc="Record timestamp.")
