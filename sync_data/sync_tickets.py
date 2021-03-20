from kivymd.uix.snackbar import Snackbar
from assets.eval_func_speed import runtime_log
from database import base
from database.model_tickets import ModelTickets
from database.model_messages import ModelMessages
from general_functions import functions
import logging
logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')

list_objects_tks = []


class SyncTickets(object):

    def __init__(self, subscription_id=None, timestamp = 0, session=None ):
        self.session = session
        self.model_tks = ModelTickets()
        self.subscription_id = subscription_id
        self.timestamp = timestamp

    def load_from_db(self):
        tickets = self.model_tks.query.filter_by(subscription_id=self.subscription_id)
        logging.info("SyncTickets load_from_db dictionary: %s ", tickets)
        return tickets

    @runtime_log
    def success(self, results=None):
        results = results
        if 'errors' in results:
            Snackbar(text=results['errors'][0]['message'], padding="20dp").open()
        else:
            tickets = results['get_tickets']['edges']
            for ticket in tickets:
                ticket = ticket['node']
                ticket['subscription_id'] = self.subscription_id
                logging.info('id ticket: %s', ticket)
                if self.timestamp == 0:
                    messages = ticket.pop('listMessage')
                self.model_tks = ModelTickets(**ticket)
                self.session.merge(self.model_tks)
            if self.timestamp == 0:
                messages = messages['edges']
                for message in messages:
                    message = message['node']
                    model_msgs = ModelMessages(**message)
                    self.session.merge(model_msgs)
            list_objects_tks.append(self.model_tks)

        return list_objects_tks





