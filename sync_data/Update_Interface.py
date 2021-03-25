import logging
import plyer


class UpdateInterface(object):
    def __init__(self, MainClass =None):
        self.main_class = MainClass

    def update_ticket_tertiary_msg(self, model_msgs, subscription_id=None, ticket_id=None ):
        if self.main_class:
            lists_instance_class_subs = self.main_class.mainNavigation.list_card_sub

            for instance_card_sub in lists_instance_class_subs:
                if instance_card_sub.id == subscription_id:
                    tertiary_text = instance_card_sub.Conversations_tks. \
                        get_tertiary_text(last_id_msg=model_msgs.id, timestamp=model_msgs.timestamp)
                    instance_card_sub.Conversations_tks. \
                        mutate_list_tickets(tertiary_text=tertiary_text, id_tk=ticket_id, timestamp=model_msgs.timestamp)
                    plyer.notification.notify(title="GuazuApp, nuevo mensaje.", message=tertiary_text)
