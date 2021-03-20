from assets.eval_func_speed import runtime_log
from sync_data.sync_tickets import SyncTickets
from sync_data.sync_messages import SyncMessages
from kivy.properties import StringProperty, ColorProperty
from kivy.uix.image import AsyncImage
from kivymd.uix.list import ThreeLineAvatarIconListItem, ILeftBody
import logging
logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')
from database import base
from sqlalchemy import desc

class AsyncImageLeftWidget(ILeftBody, AsyncImage):
    pass


class ItemTickets(ThreeLineAvatarIconListItem):
    source_img = StringProperty()
    icon_name = StringProperty()
    text = StringProperty()
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

        dict_tickets = {'view_class': 'ItemTickets', 'icon_name': 'bell',
                        'color_icon': [0.9, 1, 0.2, 1], 'source_img': '', 'text': '',
                        'secondary_text': '', 'tertiary_text': ''}

        list_dict_tickets = []

        for ticket in self.list_objects_tks:
            logging.info("ticket object %s", ticket)
            if ticket.user_id == self.account_name:
                """ take node4 for get object contact """
            else:
                if ticket.name:
                    dict_tickets['text'] = ticket.name
                if ticket.image:
                    dict_tickets['source_img'] = ticket.image
                if ticket.read:
                    dict_tickets['color_icon'] = [0, 0, 0,1]
                if ticket.
                secondary_text
                self.get_last_msg_obj(ticket.last_id_msg)
        return
    @runtime_log
    def get_last_msg_obj(self, last_id_msg):

        def show_last_msg(message):
            switcher = {
                'text': '🗨️ ' + message.text,
                'ptt': '🔊 Audio.',
                'image': '🖼️ Imagen.',
                'location': ' 📍 Locación.',
                'document': ' 📄 Documento.',
            }
            return switcher.get(message.type, "nothing")

        last_obj_msg = SyncMessages(self.sessionSQL).load_last_msg_from_db(id_message=last_id_msg)

        logging.info(" show_last_msg %s", show_last_msg(last_obj_msg))

        return show_last_msg(last_obj_msg)




    def get_contact_obj(self,contact_id_name):
        return