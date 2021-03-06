from kivymd.uix.snackbar import Snackbar
from database.model_messages import ModelMessages
import logging
logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')


class SyncMessages(object):

    def __init__(self, MainClass = None,
                 ticket_id=None,
                 timestamp=0,
                 session=None,
                 id_subscription= None):

        self.ticket_id = ticket_id
        self.timestamp = timestamp
        self.session = session
        self.subscription_id = id_subscription
        self.main_class = MainClass

    def success(self, results=None):
        new_msg = False
        model_msgs = None
        if 'errors' in results:
            logging.error(f"SyncMessage", results)
        else:
            messages = results['list_message']['edges']
            for message in messages:
                message = message['node']
                message['success'] = True
                model_msgs = ModelMessages(**message)
                check = ModelMessages.query.get(model_msgs.id)
                if check:
                    new_msg = False
                    logging.info("current message exist in db ID: %s", model_msgs.id)

                else:
                    new_msg = True
                    logging.info("Is new message ID: %s", model_msgs.id)
                    self.session.merge(model_msgs)
                    self.session.commit()

        return self.main_class.class_update_interface. \
            mutate_ticket(model_msgs=model_msgs, subscription_id=self.subscription_id, ticket_id=self.ticket_id,
                          new_msg=new_msg)
