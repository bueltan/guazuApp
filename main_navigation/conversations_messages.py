import time
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel

from assets.eval_func_speed import runtime_log
from general_functions import functions
from database.model_messages import ModelMessages
from database.model_message_temp import ModelMessagesTemp
from creating_messages.new_message import NewMessage
import logging


class MessageTextFrameTx(MDLabel):
    font_name = 'UbuntuEmoji'


class MessageTextFrameRx(MDLabel):
    font_name = 'UbuntuEmoji'


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
        self.text_message.bind(text=self.save_in_temp_tablet)

    def set_ticket(self, **kwargs):
        self.id_tk_encode = kwargs.get('id_tk')
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
        self.load_message_to_sent()
        self.class_new_message = NewMessage(subscription_id=self.subscription_id,
                                            tickets_id=self.id_tk,
                                            user_received=self.user_received,
                                            user_sent=self.user_sent,
                                            main_class=self.main_class,
                                            father_class=self)

    def load_messages_from_db(self):
        self.list_objects_msgs = ModelMessages.query.filter_by(tickets_id=self.id_tk). \
            order_by(ModelMessages.timestamp.asc())
        return self.list_objects_msgs

    def go_back(self):
        self.main_class.transition.direction = 'right'
        self.main_class.current = 'mainNavigationScreen'

    def build_data_messages(self, object_message=None):
        logging.info(f"build_data_messages: {object_message} ")
        self.list_dict_messages.clear()

        if object_message:
            self.list_objects_msgs = object_message

        if self.list_objects_msgs:
            current_account = self.main_class.account.id_name

            def build_dict_data(data_obj):
                str_time = functions.TimeFormat(data_obj.timestamp).time_am_pm()
                dict_messages = {'id_bubble': data_obj.id}
                if data_obj.type == 'text':
                    if data_obj.user_sent == current_account:
                        dict_messages['view_class'] = 'MessageTextFrameTx'
                        color_text = '696969'
                        emiter = 'Tú'
                        dict_messages['id_bubble'] = data_obj.id_bubble
                        if data_obj.success:
                            icon = '✔'
                        else:
                            icon = '🕒'
                    else:
                        dict_messages['view_class'] = 'MessageTextFrameRx'
                        color_text = 'f2ebeb'
                        icon = ''
                        emiter = data_obj.user_sent

                    dict_messages[
                        'text'] = "[size=25]" + data_obj.text + "[/size]" + "[size=14][i][color=" + color_text + "]" \
                                  + '    ' + icon + ' ~' + emiter + ' ' + \
                                  str_time + "[/color][/i][/size]"

                return dict_messages

            self.list_dict_messages[:] = [build_dict_data(msg) for msg in self.list_objects_msgs]

        return self.list_dict_messages

    """ list chat RecycleView """
    def populate_conversation(self):
        self.ids.rv_messages.data = [i for i in self.list_dict_messages]

    def update_chat(self, object_message=None):
        data_message = self.build_data_messages(object_message=object_message)
        logging.info(f"update_chat > data_message: {data_message}")

        for i, d in enumerate(data_message):
            idx = self.get_index_in_list(id_bubble=d['id_bubble'])
            if idx is not None:
                logging.info(f"update bubble > idx {idx}")
                self.ids.rv_messages.data[idx] = data_message[i]
            else:
                logging.info(f"update_chat > add new one > data_message[i] {data_message[i]}")
                self.ids.rv_messages.data.append(data_message[i])

    def get_index_in_list(self, id_bubble=None):
        logging.info(f"try to find_index id_bubble: {id_bubble}")
        if id_bubble:
            idx = [idx for idx, data in enumerate(self.ids.rv_messages.data) if data['id_bubble'] == id_bubble]
            if len(idx) > 0:
                return idx[0]
            else:
                return None
        else:
            return None

    def scroll_bottom(self):
        rv = self.ids.rv_messages
        rv.scroll_y = 0

    def put_message_in_queue(self):
        if self.text_message.text != '':
            self.main_class.playsound(effect='new_message_from_me')
            logging.info(f"put_message_in_queue: {self.id_message_temp}")
            data = self.class_new_message.create_message(id_msg=self.id_message_temp, timestamp=int(time.time()))
            self.id_message_temp = None
            self.update_chat([data[0]])
            self.main_class.class_update_interface.mutate_ticket(model_msgs=data[0],
                                                                 subscription_id=self.subscription_id,
                                                                 ticket_id=self.id_tk_encode, notify=False,
                                                                 readed=True)
            self.scroll_bottom()
            self.text_message.unbind(text=self.save_in_temp_tablet)
            self.text_message.text = ''
            self.text_message.bind(text=self.save_in_temp_tablet)

    def save_in_temp_tablet(self, instance, content=None, type='text'):
        print(content)
        if type == 'text':
            text = content
            if text is not None:
                dict_message = {'type': type, 'text': text, 'id': self.id_message_temp}
                logging.info(f"save_in_temp_tablet {dict_message}")
                self.id_message_temp = self.class_new_message. \
                    persistent_message_temp(dic_message=dict_message, id_msg=self.id_message_temp)

    def load_message_to_sent(self):
        logging.info(f"load_message_to_sent id_tk: {self.id_tk}")
        self.text_message.unbind(text=self.save_in_temp_tablet)
        self.text_message.text = ''
        self.id_message_temp = None
        message_temp = ModelMessagesTemp.query.filter_by(tickets_id=self.id_tk, timestamp=None).first()
        if message_temp:
            self.id_message_temp = message_temp.id
            if message_temp.type == 'text':
                self.text_message.text = message_temp.text
        self.text_message.bind(text=self.save_in_temp_tablet)

