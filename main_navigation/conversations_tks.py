from sync_data.sync_tickets import SyncTickets
from sync_data.sync_messages import SyncMessages
from kivy.properties import StringProperty, ColorProperty
from kivy.uix.image import AsyncImage
from kivymd.uix.list import ThreeLineAvatarIconListItem, ILeftBody
import logging
logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')
from database import base


class AsyncImageLeftWidget(ILeftBody, AsyncImage):
    pass


class itemTickets(ThreeLineAvatarIconListItem):
    source_img = StringProperty()
    name_icon = StringProperty()
    secondary_text = StringProperty()
    tertiary_text = StringProperty()
    color_icon = ColorProperty()


class ConversationTks(object):
    def __init__(self, **kwargs):
        self.subscription_id = kwargs.get('subscription_id')
        self.account_id = kwargs.get('account_id')
        self.account_name = kwargs.get('account_name')
        self.list_objects_tks = kwargs.get('list_objects_tks')
        self.sessionSQL = base.Session()

    def load_list_objects_tks_from_db(self):
        self.list_objects_tks = SyncTickets(self.subscription_id).load_from_db()
        self.build_list_data_tks()
        return

    def build_list_data_tks(self, **kwargs):
        for ticket in self.list_objects_tks:
            logging.info("ticket object %s", ticket)
            if ticket.user_id == self.account_name:
                """ take node4 for get object contact """
            else:
                pass
        return

    def get_last_msg_obj(self, last_id_msg):
        last_obj_msg = SyncMessages.load_last_msg_from_db(last_id_msg)
        logging.info("ticket object %s", last_obj_msg)
        return

    def get_contact_obj(self,contact_id_name):
        return