from database import model_messages
from database import model_message_temp
from database import model_tickets
from database import model_account
from database import model_contact
from database import model_subscription
from database.base import Session, engine, Base
Base.metadata.create_all(engine)
