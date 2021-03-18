from kivymd.uix.snackbar import Snackbar
from assets.eval_func_speed import runtime_log
from database import base
from database.model_subscription import ModelSubscriptions
from general_functions import functions

import logging
logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')


class SyncSubscriptions(object):

    def __init__(self, account_id= None):
        self.session = base.Session()
        self.model_sub = ModelSubscriptions()
        self.account_id = account_id

        self.list_sub_data = []

    def update_timestamp_sync_subs(self, timestamp, id):
        self.model_sub = self.model_sub.query.get(id)
        self.model_sub.id = id
        self.model_sub.last_sync_timestamp = timestamp
        self.session.merge(self.model_sub)
        self.session.commit()

    @runtime_log
    def success(self, results=None):

        results = results
        if 'errors' in results:
            Snackbar(text=results['errors'][0]['message'], padding="20dp").open()
        else:
            subscriptions = results['subscription_list']['edges']
            for sub in subscriptions:
                source = sub['node']['source']
                subs_id = sub['node']['id']
                subs_in_db = self.model_sub.query.get(subs_id)
                if subs_in_db :
                    self.model_sub = subs_in_db
                self.model_sub.id_account = self.account_id
                self.model_sub.source = source
                self.model_sub.id = subs_id
                self.session.merge(self.model_sub)
                data_subs = functions.get_nodes(source)
                data_subs['id'] = subs_id
                if self.model_sub.last_sync_timestamp:
                    data_subs['last_sync_timestamp'] = self.model_sub.last_sync_timestamp
                else:
                    data_subs['last_sync_timestamp'] = 0

                self.list_sub_data.append(data_subs)
        self.session.commit()
        return self.list_sub_data
