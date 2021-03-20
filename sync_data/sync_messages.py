from kivymd.uix.snackbar import Snackbar
from assets.eval_func_speed import runtime_log
from database import base
from database.model_messages import ModelMessages
from general_functions import functions

import logging
logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')


class SyncMessages(object):

    def __init__(self, ticket_id=None, timestamp=0, session=None):
        self.ticket_id = ticket_id
        self.timestamp = timestamp
        self.session = session
        self.model_msgs = ModelMessages

    def load_last_msg_from_db(self, id_message):
        id_message = functions.code('Message:' + id_message)
        logging.info("Id msg code base64: %s", id_message)
        last_msg_db = self.model_msgs.query.get(id_message)
        logging.info("Get last msg: %s", last_msg_db)
        return last_msg_db

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
        return
