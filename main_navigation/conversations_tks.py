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


class ItemTickets(ThreeLineAvatarIconListItem, AsyncImageLeftWidget):
    def __init__(self, class_main=None, **kwargs):
        super(ItemTickets, self).__init__()
        self.class_main = class_main
        self.session = base.Session()

    source_img = StringProperty()
    text = StringProperty()
    tertiary_font_style = 'UbuntuEmojiStyle'
    secondary_text = StringProperty()
    tertiary_text = StringProperty()
    color_icon = ColorProperty()
    subscription_id = StringProperty()
    user_received = StringProperty()
    user_sent = StringProperty()
    icon_name = StringProperty()
    id_tk = StringProperty()

    def open_chat(self):
        self.class_main.goto_messages(id_tk=self.id_tk,
                                      title=self.text,
                                      subscription_id=self.subscription_id,
                                      user_received=self.user_received,
                                      user_sent=self.user_sent)
        print(self.id_tk)
        self.class_main.class_update_interface. \
            mutate_ticket(ticket_id=self.id_tk,
                          subscription_id=self.subscription_id,
                          readed=True, notify=False,
                          new_msg=False)
        ticket = ModelTickets.query.get(self.id_tk)
        ticket.read = True
        self.session.merge(ticket)
        self.session.commit()
        self.session.close()


class ConversationTks(object):
    def __init__(self, Subscription):
        self.subscription_obj = Subscription
        self.sessionSQL = base.Session()
        self.subscription_id = Subscription.id
        self.account_name = Subscription.account.id_name
        self.main_class = Subscription.main_class
        self.list_objects_tks = None
        self.list_dict_tickets = []

    def load_list_objects_tks_from_db(self):
        logging.info("load_list_objects_tks_from_db subscription_id: %s", self.subscription_id)
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

            def build_dict_data(ticket):

                print("tickets_id", ticket.id)
                dict_tickets = {'subscription_id': self.subscription_id, 'view_class': 'ItemTickets',
                                'class_main': self.main_class, 'icon_name': 'bell',
                                'color_icon': [1, .8, 0, 1], 'source_img': dir_default, 'text': '',
                                'secondary_text': '', 'tertiary_text': '', 'id_tk': '', 'timestamp': 0,
                                'user_received': '', 'user_sent': ''}

                logging.info(f"for ticket in self.list_objects_tks: {ticket.id}")
                if ticket.user_id == self.account_name:
                    """ take node4 for get object contact """
                    dict_tickets['timestamp'] = ticket.timestamp
                    dict_tickets['id_tk'] = ticket.id
                    dict_tickets['user_received'] = ticket.node4
                    dict_tickets['user_sent'] = ticket.user_id
                    if ticket.name:
                        dict_tickets['text'] = ticket.node4
                    if ticket.image:
                        dict_tickets['source_img'] = ticket.image
                    if ticket.read:
                        dict_tickets['color_icon'] = [0, 0, 0, .3]
                    if '@c.us' in ticket.user_id:
                        dict_tickets['secondary_text'] = f"Desde WhatsApp {ticket.phone}"
                    if '.' == ticket.user_id[0]:
                        dict_tickets['secondary_text'] = f"Desde GuazuApp {ticket.node2}{ticket.node3}{ticket.node4}"

                    tertiary_text = self.get_tertiary_text(last_id_msg_to_encode=ticket.last_id_msg,
                                                           timestamp=ticket.timestamp)
                    dict_tickets['tertiary_text'] = tertiary_text
                else:
                    dict_tickets['timestamp'] = ticket.timestamp
                    dict_tickets['id_tk'] = ticket.id
                    dict_tickets['user_received'] = ticket.user_id
                    dict_tickets['user_sent'] = ticket.node4
                    if ticket.name:
                        dict_tickets['text'] = ticket.name
                    if ticket.image:
                        dict_tickets['source_img'] = ticket.image
                    if ticket.read:
                        dict_tickets['color_icon'] = [0, 0, 0, .3]
                    if '@c.us' in ticket.user_id:
                        dict_tickets['secondary_text'] = f"Desde WhatsApp {ticket.phone}"
                    if '.' == ticket.user_id[0]:
                        dict_tickets['secondary_text'] = f"Desde GuazuApp {ticket.node2}{ticket.node3}{ticket.user_id}"

                    tertiary_text = self.get_tertiary_text(last_id_msg_to_encode=ticket.last_id_msg,
                                                           timestamp=ticket.timestamp)
                    dict_tickets['tertiary_text'] = tertiary_text

                return dict_tickets

            self.list_dict_tickets = [build_dict_data(ticket) for ticket in self.list_objects_tks]

            logging.error("list_objects_tks is empty")

        return self.list_dict_tickets

    def get_tertiary_text(self, last_id_msg_to_encode=None, last_id_msg=None, timestamp=0):
        str_time = functions.TimeFormat(timestamp).date_with_days_es()

        def show_last_msg(message):
            switcher = {
                'text': '‍️🗨 ' + str_time + '| ' + message.text,
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

    def get_contact_obj(self, contact_id_name):
        """is necessary when the ticket is created for my , work in this ! """
        return

    def mutate_list_tickets(self, list_dict_tickets=None,
                            tertiary_text=None,
                            color_icon=None,
                            timestamp=0,
                            id_tk=None):

        logging.info(f"mutate_list_tickets list_dict_tickets:  {list_dict_tickets}, "
                     f"tertiary_text: {tertiary_text}, color_icon: {color_icon},"
                     f"timestamp: {timestamp}, id_tk: {id_tk}")

        if list_dict_tickets:
            self.list_dict_tickets = list_dict_tickets

        if not self.list_dict_tickets:
            self.build_list_data_tks()

        if self.list_dict_tickets:

            def find_index(list_data=self.subscription_obj.ids.rv.data, id_tk=None):
                logging.info(f"try to find_index id_tk: {id_tk}")
                if id_tk:
                    idx = [idx for idx, tk in enumerate(list_data) if tk['id_tk'] == id_tk]
                    if len(idx) > 0:
                        return idx[0]
                        logging.info(f"found id_tk: {id_tk}")

                    else:
                        return None

            def update_tickets(index=None, tertiary=None, time=0):
                logging.info(f"update_tickets index: {index},"
                             f" tertiary_text: {tertiary},"
                             f" color_icon: {color_icon}")

                if index is not None and tertiary is not None:
                    logging.info("update tertiary")
                    self.subscription_obj.ids.rv.data[index]['tertiary_text'] = tertiary
                    self.subscription_obj.ids.rv.data[index]['timestamp'] = time
                    self.subscription_obj.ids.rv.data[index]['color_icon'] = [1, .8, 0, 1]

                if index is not None and color_icon is not None:
                    logging.info("update color_icon")
                    self.subscription_obj.ids.rv.data[index]['color_icon'] = color_icon

                if index is None:
                    logging.info("load all list_dict_tickets ")
                    self.build_list_data_tks()
                    for i, d in enumerate(self.list_dict_tickets):
                        idx = find_index(id_tk=self.list_dict_tickets[i]['id_tk'])
                        if idx is not None:
                            update_tickets(index=idx,
                                           tertiary=self.list_dict_tickets[i]['tertiary_text'],
                                           time=self.list_dict_tickets[i]['timestamp'])
                        else:
                            self.subscription_obj.ids.rv.data.append(self.list_dict_tickets[i])

            if id_tk is not None:
                index = find_index(id_tk=id_tk)
                update_tickets(index=index, tertiary=tertiary_text, time=timestamp)
            else:
                update_tickets()
        self.subscription_obj.ids.rv.data.sort(key=lambda x: x['timestamp'], reverse=True)
        self.subscription_obj.ids.rv.refresh_from_data()

    def search(self, text=""):
        self.subscription_obj.ids.rv.data = []
        for i, d in enumerate(self.list_dict_tickets):
            if text.lower() in d['secondary_text'].lower() \
                        or text in d['text'].lower() or text in d['tertiary_text'].lower():
                self.subscription_obj.ids.rv.data.append(self.list_dict_tickets[i])
            else:
                logging.info("is time to try find looking more deeper")
