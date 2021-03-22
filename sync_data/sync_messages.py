from kivymd.uix.snackbar import Snackbar
from assets.eval_func_speed import runtime_log
from database.model_messages import ModelMessages

import logging
logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')


class SyncMessages(object):

    def __init__(self, MainClass=None, ticket_id=None, timestamp=0, session=None, id_subscription= None):
        self.ticket_id = ticket_id
        self.timestamp = timestamp
        self.session = session
        self.model_msgs = ModelMessages
        self.main_class = MainClass
        self.subscription_id = id_subscription

    def update_ticket_tertiary_msg(self, model_msgs):
        if self.main_class:

            lists_instance_class_subs = self.main_class.mainNavigation.list_card_sub
            logging.info("conteiner_cards_subscriptions %s", lists_instance_class_subs)
            for instance_card_sub in lists_instance_class_subs:
                if instance_card_sub.id == self.subscription_id:
                    tertiary_text = instance_card_sub.Conversations_tks.get_tertiary_text(last_id_msg=model_msgs.id)
                    instance_card_sub.Conversations_tks.mutate_list_tickets(tertiary_text=tertiary_text, id_tk=self.ticket_id)


    @runtime_log
    def success(self, results=None):
        logging.info("result success messages %s", results)
        if 'errors' in results:
            Snackbar(text=results['errors'][0]['message'], padding="20dp").open()
        else:
            messages = results['list_message']['edges']
            for message in messages:
                message = message['node']
                model_msgs = ModelMessages(**message)
                self.session.merge(model_msgs)
                self.update_ticket_tertiary_msg(model_msgs)
        return
