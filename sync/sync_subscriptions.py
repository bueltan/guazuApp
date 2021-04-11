from kivymd.uix.snackbar import Snackbar
from database.model_subscription import ModelSubscriptions
import logging
logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')


class SyncSubscriptions(object):

    def __init__(self, MainClass=None, account_obj=None, account_id=None, session=None):
        self.model_sub = ModelSubscriptions()
        self.account_obj = account_obj
        self.account_id = account_id
        self.session = session
        self.main_class = MainClass

    def update_timestamp_sync_subs(self, timestamp, id):
        logging.info("begin Update_timestamp_sync_subs %s", timestamp)
        self.model_sub = self.model_sub.query.get(id)
        self.model_sub.id = id
        self.model_sub.last_sync_timestamp = timestamp
        self.session.merge(self.model_sub)
        logging.info("end Update_timestamp_sync_subs %s", timestamp)

    def create_subscription_interfaces(self):
        if self.main_class:
            logging.info("MainClass type: %s", type(self.main_class))
            self.main_class.class_main_navigation.build_card_subscription(account=self.account_obj, subscription=self.model_sub)


    async def success(self, results=None):
        list_object_subscription = []
        logging.info("Result success  SyncSubscriptions %s", results)
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
                    self.session.commit()
                    self.create_subscription_interfaces()
                    await self.main_class.open_tunnel(subscription_id=subs_from_sever.id, timestamp= 0)
                list_object_subscription.append(self.model_sub)
            logging.info(" LIST OBJECT SUBSCRIPTIONS %s", list_object_subscription)

            return list_object_subscription
