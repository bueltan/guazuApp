from assets.eval_func_speed import runtime_log
from database.model_messages import ModelMessages
from database.model_tickets import ModelTickets
from general_functions import functions
from kivy.properties import StringProperty, ColorProperty
from kivy.uix.image import AsyncImage
from kivymd.uix.list import ThreeLineAvatarIconListItem, ILeftBody
from database import base
from path import assets
import logging

logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')


class AsyncImageLeftWidget(ILeftBody, AsyncImage):
    pass


class ItemTickets(ThreeLineAvatarIconListItem):
    tertiary_font_name = 'UbuntuEmoji'
    source_img = StringProperty()
    icon_name = StringProperty()
    text = StringProperty()
    secondary_text = StringProperty()
    tertiary_text = StringProperty()
    color_icon = ColorProperty()


class ConversationTks(object):
    def __init__(self, Subscription):
        self.subscription_obj = Subscription
        self.sessionSQL = base.Session()
        self.subscription_id = Subscription.id
        self.account_name = Subscription.account.id_name
        self.list_objects_tks = None
        self.list_dict_tickets = None

    def load_list_objects_tks_from_db(self):
        self.list_objects_tks = ModelTickets.query.filter_by(subscription_id=self.subscription_id). \
            order_by(ModelTickets.timestamp.desc())
        logging.info("SyncTickets load_from_db dictionary: %s ", self.list_objects_tks)
        return

    def build_list_data_tks(self, list_objects_tks=None):
        if list_objects_tks:
            self.list_objects_tks = list_objects_tks
        else:
            self.load_list_objects_tks_from_db()
        if self.list_objects_tks:
            self.list_dict_tickets = []

            dir_default = assets + "/img_profile/default_profile.png"
            dict_tickets = {'view_class': 'ItemTickets', 'icon_name': 'bell',
                            'color_icon': [0.9, 1, 0.2, 1], 'source_img': dir_default, 'text': '',
                            'secondary_text': '', 'tertiary_text': '', 'id_tk': ''}

            for ticket in self.list_objects_tks:
                print("ticket---", ticket.user_id)
                logging.info("ticket object %s", ticket)
                if ticket.user_id == self.account_name:
                    """ take node4 for get object contact """
                else:
                    dict_tickets['id_tk'] = ticket.id
                    if ticket.name:
                        dict_tickets['text'] = ticket.name
                    if ticket.image:
                        dict_tickets['source_img'] = ticket.image
                    if ticket.read:
                        dict_tickets['color_icon'] = [0, 0, 0, 1]
                    if '@c.us' in ticket.user_id:
                        dict_tickets['secondary_text'] = f"Desde WhatsApp {ticket.phone}"
                    if '.' == ticket.user_id[0]:
                        dict_tickets['secondary_text'] = f"Desde GuazuApp {ticket.node2}{ticket.node3}{ticket.user_id}"
                    tertiary_text = self.get_tertiary_text(last_id_msg_to_encode= ticket.last_id_msg)
                    dict_tickets['tertiary_text'] = tertiary_text
                    self.list_dict_tickets.append(dict_tickets)

            logging.info(f"len self.list_dict_tickets: {len(self.list_dict_tickets)}, list: {self.list_dict_tickets}")
        else:
            logging.error("list_objects_tks is empty")

        return self.list_dict_tickets

    @runtime_log
    def get_tertiary_text(self, last_id_msg_to_encode=None, last_id_msg=None ):

        def show_last_msg(message):
            switcher = {
                'text': '‍️🗨 ' + message.text,
                'ptt': '🔊 Audio.',
                'image': '🖼️ Imagen.',
                'location': ' 📍 Locación.',
                'document': ' 📄 Documento.',
            }
            return switcher.get(message.type, "nothing")
        if last_id_msg_to_encode:

            id_message = functions.code('Message:' + last_id_msg_to_encode)
            logging.info("Id msg code base64: %s", id_message)
        else:
            id_message = last_id_msg

        last_obj_msg = ModelMessages.query.get(id_message)
        logging.info("Get last msg: %s", last_obj_msg)

        if last_obj_msg:
            return show_last_msg(last_obj_msg)
        else:
            return '‍️🗨 ... '
        logging.info(" show_last_msg %s", show_last_msg(last_obj_msg))

    """is necessary when the ticket is created for my , work in this ! """

    def get_contact_obj(self, contact_id_name):
        return

    def mutate_list_tickets(self, list_dict_tickets=None,
                            text="",
                            search=False,
                            tertiary_text=None,
                            color_icon=None,
                            id_tk=None):

        if list_dict_tickets:
            self.list_dict_tickets = list_dict_tickets

        else:
            if not self.list_dict_tickets:
                self.build_list_data_tks()

        if self.list_dict_tickets:

            def find_index(list=self.subscription_obj.ids.rv.data, id_tk=None):
                logging.info(f"try to find existent ticket with id {id_tk} in {list} ")
                if id_tk:
                    for index, tk in enumerate(list):
                        found = (tk['id_tk'] == id_tk)
                        logging.info("Found %s ", found)
                        if found:
                            return index
                        else:
                            return None

            def update_tickets(index=None, tertiary_text=None):

                if index is not None:
                    logging.info("We found the tk_id index:, updated %s", index)
                    self.subscription_obj.ids.rv.data[index]['tertiary_text'] = tertiary_text
                    if color_icon is not None:
                        self.subscription_obj.ids.rv.data[index]['color_icon'] = color_icon
                    self.subscription_obj.ids.rv.refresh_from_data()
                else:
                    for i, d in enumerate(self.list_dict_tickets):
                        if search:
                            if (text).lower() in d['secondary_text'].lower() \
                                    or text in d['text'].lower() or text in d['tertiary_text'].lower():
                                self.subscription_obj.ids.rv.data.append(self.list_dict_tickets[i])
                        else:
                            logging.info("new tk")
                            self.subscription_obj.ids.rv.data.append(self.list_dict_tickets[i])

            if id_tk is not None:
                index = find_index(id_tk=id_tk)
                update_tickets(index=index, tertiary_text=tertiary_text)
            else:
                for ticket_dict in self.list_dict_tickets:
                    index = find_index(id_tk=ticket_dict['id_tk'])
                    update_tickets(index=index, tertiary_text=ticket_dict['tertiary_text'])



