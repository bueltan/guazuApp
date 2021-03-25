from datetime import datetime

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
    text = StringProperty()
    secondary_text = StringProperty()
    tertiary_text = StringProperty()
    color_icon = ColorProperty()
    source_img = StringProperty()
    icon_name = StringProperty()


class ConversationTks(object):
    def __init__(self, Subscription):
        self.subscription_obj = Subscription
        self.sessionSQL = base.Session()
        self.subscription_id = Subscription.id
        self.account_name = Subscription.account.id_name
        self.list_objects_tks = None
        self.list_dict_tickets = []
        self.day_week = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        self.dias_semanas = ['lun', 'mar', 'mie', 'jue', 'vie', 'sab', 'dom']

    def load_list_objects_tks_from_db(self):
        self.list_objects_tks = ModelTickets.query.filter_by(subscription_id=self.subscription_id). \
            order_by(ModelTickets.timestamp.desc())

    def build_list_data_tks(self, list_objects_tks=None):
        if list_objects_tks:
            self.list_objects_tks = list_objects_tks
        else:
            self.load_list_objects_tks_from_db()

        if self.list_objects_tks:
            self.list_dict_tickets.clear()

            dir_default = assets + "/img_profile/default_profile.png"

            for ticket in self.list_objects_tks:
                dict_tickets = {'view_class': 'ItemTickets', 'icon_name': 'bell',
                                'color_icon': [0.9, 1, 0.2, 1], 'source_img': dir_default, 'text': '',
                                'secondary_text': '', 'tertiary_text': '', 'id_tk': '', 'timestamp': 0}

                logging.info(f"for ticket in self.list_objects_tks: {ticket.id}")
                if ticket.user_id == self.account_name:
                    """ take node4 for get object contact """
                else:
                    dict_tickets['timestamp'] = ticket.timestamp
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

                    tertiary_text = self.get_tertiary_text(last_id_msg_to_encode=ticket.last_id_msg, timestamp=ticket.timestamp)
                    dict_tickets['tertiary_text'] = tertiary_text

                self.list_dict_tickets.append(dict_tickets)
        else:
            logging.error("list_objects_tks is empty")


        return self.list_dict_tickets

    @runtime_log
    def get_tertiary_text(self, last_id_msg_to_encode=None, last_id_msg=None, timestamp=0):
        dt_object = datetime.fromtimestamp(timestamp)
        str_time =dt_object.strftime(" %a %d %H:%M |")

        for index, day in enumerate(self.day_week):
            if day in str_time:
                str_time = str_time.replace(day, self.dias_semanas[index])
                break

        def show_last_msg(message):
            switcher = {
                'text': '‍️🗨 ' + str_time + ' ' + message.text,
                'ptt': '🔊 ' + str_time + ' ' + 'Audio.',
                'image': '🖼️ ' + str_time + ' ' + ' Imagen.',
                'location': ' 📍 ' + str_time + ' ' + ' Locación.',
                'document': ' 📄 ' + str_time + ' ' + ' Documento.',
            }
            return switcher.get(message.type, "nothing")

        if last_id_msg_to_encode:

            id_message = functions.encode('Message:' + last_id_msg_to_encode)
            logging.info("Id msg encode base64: %s", id_message)
        else:
            id_message = last_id_msg

        last_obj_msg = ModelMessages.query.get(id_message)
        logging.info("Get last msg: %s", last_obj_msg)

        if last_obj_msg:
            return show_last_msg(last_obj_msg)
        else:
            return '‍️🗨 ' + str_time + '... '

    """is necessary when the ticket is created for my , work in this ! """

    def get_contact_obj(self, contact_id_name):
        return

    def mutate_list_tickets(self, list_dict_tickets=None,
                            tertiary_text=None,
                            color_icon=None,
                            timestamp= 0,
                            id_tk=None):


        if list_dict_tickets:
            self.list_dict_tickets = list_dict_tickets
        else:
            if not self.list_dict_tickets:
                self.build_list_data_tks()

        if self.list_dict_tickets:

            def find_index(list=self.subscription_obj.ids.rv.data, id_tk=None):
                if id_tk:
                    for index, tk in enumerate(list):
                        found = (tk['id_tk'] == id_tk)
                        if found:
                            return index
                    else:
                        return None

            def update_tickets(index=None, tertiary_text=None):
                if index is not None:
                    self.subscription_obj.ids.rv.data[index]['tertiary_text'] = tertiary_text
                    self.subscription_obj.ids.rv.data[index]['timestamp'] = timestamp

                    if color_icon is not None:
                        self.subscription_obj.ids.rv.data[index]['color_icon'] = color_icon
                else:
                    for i, d in enumerate(self.list_dict_tickets):
                        self.subscription_obj.ids.rv.data.append(self.list_dict_tickets[i])



            if id_tk is not None:
                index = find_index(id_tk=id_tk)
                update_tickets(index=index, tertiary_text=tertiary_text)
            else:
                for ticket_dict in self.list_dict_tickets:
                    index = find_index(id_tk=ticket_dict['id_tk'])
                    update_tickets(index=index, tertiary_text=ticket_dict['tertiary_text'])
                    if index == None:
                        break

        self.subscription_obj.ids.rv.data.sort(key=lambda x: x['timestamp'], reverse=True)

    def search(self, text=""):
        self.subscription_obj.ids.rv.data = []
        for i, d in enumerate(self.list_dict_tickets):
            if (text).lower() in d['secondary_text'].lower() \
                        or text in d['text'].lower() or text in d['tertiary_text'].lower():
                    self.subscription_obj.ids.rv.data.append(self.list_dict_tickets[i])
            else:
                logging.info("is time to try find looking more deeper")












