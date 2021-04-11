from .base import Base
from sqlalchemy import Column, String, Integer, ForeignKey, Boolean


class ModelMessagesTemp(Base):
    """MessagesTemp model."""

    __tablename__ = 'MessagesTemp'
    id = Column('id', String(40), primary_key=True, doc="Id of the MessageSent.")
    subscription_id = Column('subscription_id', String(40))
    tickets_id = Column('tickets_id', String(40), doc="Id of the Tickets")
    user_received = Column('user_received', String(30), doc=" user_received.")
    user_sent = Column('user_sent', String(30), doc=" user_sent.")
    type = Column('type', String(15), nullable=False, doc="Type of the message.")
    text = Column('text', String(15000), doc="Text of the massage max len 6000")
    mime = Column('mime', String(50), doc="format of the media data")
    url = Column('url', String(200), doc="url of file")
    caption = Column('caption', String(200), doc="caption of the message")
    filename = Column('filename', String(150), doc="name of the file ")
    payload = Column('payload', String(100), doc="Latitude and longitude")
    vcardList = Column('vcardList', String(1000), doc="List of the vcard")
    timestamp = Column('timestamp', Integer, doc="time in touch button sent")
