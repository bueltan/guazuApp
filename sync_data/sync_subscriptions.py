from kivymd.uix.snackbar import Snackbar
from assets.eval_func_speed import runtime_log
from database.model_subscription import ModelSubscriptions
from general_functions import functions

import logging
logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')


class SyncSubscriptions(object):

    def __init__(self, account_id=None, session=None):
        self.model_sub = ModelSubscriptions()
        self.account_id = account_id
        self.session = session

    def load_from_db(self):
        subs_from_db = self.model_sub.query.filter_by(id_account=functions.decode(self.account_id))
        logging.info("SyncSubscriptions get from db account id: %s", functions.decode(self.account_id))
        return subs_from_db

    def update_timestamp_sync_subs(self, timestamp, id):
        self.model_sub = self.model_sub.query.get(id)
        self.model_sub.id = id
        self.model_sub.last_sync_timestamp = timestamp
        self.session.merge(self.model_sub)
        logging.info(" Update_timestamp_sync_subs %s")

    @runtime_log
    def success(self, results=None):
        list_object_subscription = []
        logging.info("Result success subscriptions %s", results)
        if 'errors' in results:
            Snackbar(text=results['errors'][0]['message'], padding="20dp").open()
        else:
            subscriptions = results['subscription_list']['edges']
            for subscription in subscriptions:
                subscription = subscription['node']
                subs_id = subscription['id']
                subs_from_sever = ModelSubscriptions(**subscription)
                self.model_sub = self.model_sub.query.get(subs_id)
                if self.model_sub:
                    if self.model_sub.source != subs_from_sever.source:
                        logging.info("MODEL SUBSCRIPTION HAS CHANGES ID : %s", subs_id)
                        self.model_sub = subs_from_sever
                        self.session.merge(self.model_sub)
                    else:
                        logging.info("MODEL SUBSCRIPTION IS CURRENT UPDATED ID : %s ", subs_id)
                else:
                    logging.info("NEW SUBSCRIPTION ID : %s ", subs_id)
                    subs_from_sever.last_sync_timestamp = 0
                    self.session.add(subs_from_sever)
                    self.model_sub = subs_from_sever

                list_object_subscription.append(self.model_sub)
            logging.info(" LIST OBJECT SUBSCRIPTIONS %s", list_object_subscription)

            return list_object_subscription