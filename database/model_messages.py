from .base import Base
from sqlalchemy import Column, String, Integer, ForeignKey, Boolean


class ModelMessages(Base):
    """Messages model."""

    __tablename__ = 'Messages'
    id = Column('id', String(80), primary_key=True, doc="Id of the MessageSent.")
    tickets_id = Column('tickets_id', ForeignKey('Tickets.id'), doc="Id of the Tickets")
    id_bubble = Column('id_bubble', String(40), doc="id from temp message")
    type = Column('type', String(15), nullable=False, doc="Type of the message.")
    text = Column('text', String(15000), doc="Text of the massage max len 6000")
    fromMe = Column('fromMe', Boolean, doc="is the message from me.")
    _serialized = Column('_serialized', String(80), doc="_serialized")
    mime = Column('mime', String(50), doc="format of the media data")
    url = Column('url', String(200), doc="url of file")
    caption = Column('caption', String(200), doc="caption of the message")
    filename = Column('filename', String(150), doc="name of the file ")
    payload = Column('payload', String(100), doc="Latitude and longitude")
    vcardList = Column('vcardList', String(1000), doc="List of the vcard")
    timestamp = Column('timestamp', Integer, doc="Record timestamp.")
    success = Column('success',
                     Boolean,
                     doc="if this message is received for the server ")
    success_api = Column('success_api', Boolean,
                     doc="if this message is received for the external api")

    user_received = Column('user_received', String(30), doc=" user_received.")
    user_sent = Column('user_sent', String(30), doc=" user_sent.")

