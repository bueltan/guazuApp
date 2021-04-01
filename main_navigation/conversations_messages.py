import time
from abc import ABC

from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivy.animation import Animation
from general_functions import functions
from database.model_messages import ModelMessages
from database.model_message_temp import ModelMessagesTemp
from creating_messages.new_message import NewMessage
import logging


class MessageTextFrameTx(MDLabel):
    def __init__(self, mainwid=None):
        super(MessageTextFrameTx, self).__init__()
        self.mainwid = mainwid
        self.markup = True
        self.font_name = 'UbuntuEmoji'


class MessageTextFrameRx(MDLabel):
    def __init__(self, mainwid=None):
        super(MessageTextFrameRx, self).__init__()
        self.mainwid = mainwid
        self.markup = True
        self.font_name = 'UbuntuEmoji'


class MessagesScreen(MDBoxLayout):
    def __init__(self, MainClass=None, **kwargs):
        super(MessagesScreen, self).__init__()
        self.main_class = MainClass
        self.title = ''
        self.id_tk = None
        self.list_objects_msgs = None
        self.list_dict_messages = []
        self.subscription_id = None
        self.id_message_temp = None
        self.user_received = None
        self.class_new_message = None
        self.id_tk_encode = None

    def set_ticket(self, **kwargs):
        self.id_tk_encode = kwargs.get('id_tk')
        print("id_tk_encode: ", self.id_tk_encode)
        self.id_tk = functions.decode(self.id_tk_encode)
        self.title = kwargs.get('title')
        """ data for create new message """
        self.subscription_id = kwargs.get('subscription_id')
        self.user_received = kwargs.get('user_received')
        self.user_sent = kwargs.get('user_sent')
        self.list_objects_msgs = []
        self.list_dict_messages = []
        self.load_messages_from_db()
        self.build_data_messages()
        self.populate_conversation()
        self.scroll_bottom()
        self.class_new_message = NewMessage(subscription_id=self.subscription_id,
                                            tickets_id=self.id_tk,
                                            user_received=self.user_received,
                                            user_sent=self.user_sent)
        self.load_message_to_sent()

    def load_messages_from_db(self):
        self.list_objects_msgs = ModelMessages.query.filter_by(tickets_id=self.id_tk). \
            order_by(ModelMessages.timestamp.asc())
        return self.list_objects_msgs

    def go_back(self):
        self.main_class.transition.direction = 'right'
        self.main_class.current = 'mainNavigationScreen'

    def build_data_messages(self, object_message= None):
        self.list_dict_messages.clear()
        if object_message:
            self.list_objects_msgs = object_message

        if self.list_objects_msgs:
            print("build_data_messages")
            for messages in self.list_objects_msgs:
                str_time = functions.TimeFormat(messages.timestamp).time_am_pm()
                dict_messages = {'view_class': '', 'class_main': self.main_class,
                                 'text': ''}
                if messages.type == 'text':
                    if messages.user_sent == self.main_class.account.id_name:
                        dict_messages['view_class'] = 'MessageTextFrameTx'
                        color_text = '696969'
                        emiter = 'Tú'
                        if messages.success == True:
                            icon = '✔'
                        else:
                            icon = '🕒'
                    else:
                        dict_messages['view_class'] = 'MessageTextFrameRx'
                        color_text = 'f2ebeb'
                        icon = ''
                        emiter = messages.user_sent
                    dict_messages['text'] = messages.text + "[size=12][i][color="+color_text+"]"\
                                            +'    '+ icon +' ~' + emiter + ' ' +\
                                            str_time + "[/color][/i][/size]"
                self.list_dict_messages.append(dict_messages)

        return self.list_dict_messages

    def populate_conversation(self):
        self.ids.rv_messages.data = []
        for i, d in enumerate(self.list_dict_messages):
            self.ids.rv_messages.data.append(self.list_dict_messages[i])

    def update_chat(self, object_message=None):
        data_message = self.build_data_messages(object_message=object_message)
        for i, d in enumerate(data_message):
            self.ids.rv_messages.data.append(data_message[i])

    def scroll_bottom(self):
        rv = self.ids.rv_messages
        Animation.cancel_all(rv, 'scroll_y')
        Animation(scroll_y=0, t='out_quad', d=.1).start(rv)

    def put_message_in_queue(self):
        if self.text_message.text != '':
            logging.info(f"put_message_in_queue: {self.id_message_temp}")
            data = self.class_new_message.sent_message_temp(id_msg=self.id_message_temp, timestamp=int(time.time()))
            self.text_message.text = ''
            self.id_message_temp = None
            self.update_chat([data[0]])
            self.main_class.class_update_interface.mutate_ticket(model_msgs=data[0],
                                                                 subscription_id=self.subscription_id,
                                                                 ticket_id=self.id_tk_encode, notify=False,
                                                                 readed=True)

            self.scroll_bottom()

    def save_in_temp_tablet(self, type='text', content=None):
        if type == 'text':
            text = content
            if text != '':
                dict_message = {'type': type, 'text': text, 'id': self.id_message_temp}
                logging.info(f"save_in_temp_tablet {dict_message}")
                self.id_message_temp = self.class_new_message.\
                    persistent_message_temp(dic_message=dict_message, id_msg=self.id_message_temp)

    def load_message_to_sent(self):
        logging.info(f"my id_tk: {self.id_tk}")
        self.text_message.text = ''
        self.id_message_temp = None
        message_temp = ModelMessagesTemp.query.filter_by(tickets_id=self.id_tk, timestamp=None).first()
        if message_temp:
            self.id_message_temp = message_temp.id
            if message_temp.type == 'text':
                self.text_message.text = message_temp.text

