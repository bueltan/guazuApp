import plyer
from kivymd.uix.snackbar import Snackbar
from assets.eval_func_speed import runtime_log
from database.model_messages import ModelMessages
import logging
logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')


class SyncMessages(object):

    def __init__(self, MainClass = None, ticket_id=None, timestamp=0, session=None, id_subscription= None):
        self.ticket_id = ticket_id
        self.timestamp = timestamp
        self.session = session
        self.model_msgs = ModelMessages
        self.subscription_id = id_subscription
        self.main_class = MainClass

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
                check = ModelMessages.query.get(model_msgs.id)
                if check:
                    logging.info("current message exist in db ID: %s", model_msgs.id)
                else:
                    logging.info("Is new message ID: %s", model_msgs.id)

                    self.session.merge(model_msgs)
                    self.session.commit()

        return self.main_class.Update_interface.\
                        update_ticket_tertiary_msg(subscription_id=self.subscription_id,
                                                   ticket_id=self.ticket_id, model_msgs=model_msgs)
