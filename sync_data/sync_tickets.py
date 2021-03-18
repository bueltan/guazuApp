from kivymd.uix.snackbar import Snackbar
from assets.eval_func_speed import runtime_log
from database import base
from database.model_tickets import ModelTickets
from general_functions import functions

import logging
logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')


class SyncTickets(object):

    def __init__(self, subscription_id=None):
        self.session = base.Session()
        self.model_tks = ModelTickets()
        self.subscription_id = subscription_id

        self.list_tks={}


    @runtime_log
    def success(self, results=None):
        results = results
        if 'errors' in results:
            Snackbar(text=results['errors'][0]['message'], padding="20dp").open()
        else:
            tickets = results['ticket_list']['edges']
            for ticket in tickets:
                ticket = ticket['node']
                print(ticket)
                id = ticket['id']
                logging.debug('id ticket: %s', id)
                self.model_tks = ModelTickets(**ticket)
                self.list_tks[id]= ticket.__d
            self.session.merge(self.model_tks)
            self.session.commit
            print(self.list_tks)
        return





