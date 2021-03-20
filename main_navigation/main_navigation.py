""" MainNavigation """
from kivymd.uix.navigationdrawer import MDNavigationLayout

from main_navigation.card_subscription import CardSubscription
from sync_data.sync_data import SyncSubscriptions
from database import base
import logging
logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')


class MainNavigation(MDNavigationLayout):
    """ MainNavigation """
    def __init__(self, **kwargs):
        super(MainNavigation, self).__init__()
        logging.info("MainNavigation")
        self.sessionSQL = base.Session()

    def load_subscriptions_from_db(self, account=None):
        logging.info("load_subscriptions_from_db Account: %s", account)
        if account:
            subscriptions = SyncSubscriptions(account_id=account.id, session=self.sessionSQL).load_from_db()
            for subscription in subscriptions:
                logging.info("load_subscriptions_from_db subscription %s", subscription)
                self.build_card_subscription(subscription=subscription, account=account)

    def build_card_subscription(self, **kwargs):
        """ subscription and account object required"""
        card_sub = CardSubscription(**kwargs)
        self.container.add_widget(card_sub)










