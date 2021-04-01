from kivymd.uix.snackbar import Snackbar
from assets.eval_func_speed import runtime_log
from database.model_tickets import ModelTickets
from database.model_messages import ModelMessages
import logging
logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')

list_objects_tks = []


class SyncTickets(object):

    def __init__(self, MainClass=None, subscription_id=None, timestamp=0, session=None):
        """
        :type MainClass: object

        """
        self.session = session
        self.model_tks = ModelTickets()
        self.subscription_id = subscription_id
        self.timestamp = timestamp
        self.main_class = MainClass

    def update_list_objects_tks(self, model_tks):
        if self.main_class:
            lists_instance_class_subs = self.main_class.class_main_navigation.list_card_sub
            for instance_card_sub in lists_instance_class_subs:
                if instance_card_sub.id == self.subscription_id:
                    list_dict_tks = instance_card_sub.Conversations_tks.build_list_data_tks(model_tks)
                    instance_card_sub.Conversations_tks.mutate_list_tickets(list_dict_tks)

    @runtime_log
    def success(self, results=None):
        results = results
        if 'errors' in results:
            Snackbar(text=results['errors'][0]['message'], padding="20dp").open()
        else:
            tickets = results['get_tickets']['edges']
            for ticket in tickets:
                ticket = ticket['node']
                ticket['read'] = False
                ticket['subscription_id'] = self.subscription_id
                if self.timestamp == 0:
                    messages = ticket.pop('listMessage')
                    self.model_tks = ModelTickets(**ticket)
                    self.session.merge(self.model_tks)
                    list_objects_tks.append(self.model_tks)

                    messages = messages['edges']
                    for message in messages:
                        message = message['node']
                        model_msgs = ModelMessages(**message)
                        self.session.merge(model_msgs)
                        self.session.commit()
                else:
                    ticket_from_db = ModelTickets.query.filter_by(id=ticket['id'],
                                                                  last_id_msg=ticket['last_id_msg']).first()
                    if not ticket_from_db:
                        self.model_tks = ModelTickets(**ticket)
                        self.session.merge(self.model_tks)
                        list_objects_tks.append(self.model_tks)
                        self.session.commit()


            if list_objects_tks:
                self.update_list_objects_tks(list_objects_tks)

            return list_objects_tks





