import logging
import plyer


class UpdateInterface(object):
    def __init__(self, MainClass=None):
        self.main_class = MainClass

    def mutate_ticket(self, model_msgs=None, subscription_id=None,
                      ticket_id=None, new_msg=True, notify=True, readed=None):

        logging.info(f"mutate_ticket model_msgs: {model_msgs},"
                     f" subscription_id : {subscription_id}, ticket_id: {ticket_id},"
                     f" notify: {notify}, readed :{readed}")

        if self.main_class:
            lists_instance_class_subs = self.main_class.class_main_navigation.list_card_sub
            for instance_card_sub in lists_instance_class_subs:
                if instance_card_sub.id == subscription_id:
                    if new_msg:
                        if model_msgs.user_sent == self.main_class.account.id_name:
                            notify = False
                        tertiary_text = instance_card_sub.Conversations_tks. \
                            get_tertiary_text(last_id_msg=model_msgs.id, timestamp=model_msgs.timestamp)
                        instance_card_sub.Conversations_tks. \
                            mutate_list_tickets(tertiary_text=tertiary_text, id_tk=ticket_id,
                                                timestamp=model_msgs.timestamp)
                        if notify:
                            plyer.notification.notify(title="GuazuApp, mensaje.", message=tertiary_text)

                    if readed:
                        instance_card_sub.Conversations_tks.\
                            mutate_list_tickets(color_icon=[0, 0, 0, .3],
                                                id_tk=ticket_id)

    def update_current(self, id_tk_encode=None, message_obj=None, subscription_id=None):

        if self.main_class.current == 'MessagesScreen':
            if self.main_class.class_screen_messages.id_tk_encode == id_tk_encode:
                self.main_class.playsound(effect='new_bubble')
                self.main_class.class_screen_messages.update_chat(object_message=[message_obj])
                if subscription_id is not None:
                    self.mutate_ticket(subscription_id=subscription_id, readed=True, ticket_id=id_tk_encode,
                                       notify=False, new_msg=False)
