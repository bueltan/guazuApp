""" MainNavigation """
from kivymd.uix.navigationdrawer import MDNavigationLayout
from assets.eval_func_speed import runtime_log
from general_functions import functions
from main_navigation.card_subscription import CardSubscription
from database.model_subscription import ModelSubscriptions
import logging
logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')


class MainNavigation(MDNavigationLayout):
    """ MainNavigation """
    def __init__(self, **kwargs):
        super(MainNavigation, self).__init__()
        logging.info("MainNavigation")
        self.list_card_sub = []

    @runtime_log
    def load_subscriptions_from_db(self, account=None):
        logging.info("load_subscriptions_from_db Account: %s", account)
        if account:
            subscriptions = ModelSubscriptions.query.filter_by(id_account=functions.decode(account.id))
            for subscription in subscriptions:
                logging.info("load_subscriptions_from_db subscription %s", subscription)
                self.build_card_subscription(subscription=subscription, account=account)

    def build_card_subscription(self, **kwargs):
        """ subscription and account object required"""
        card_sub = CardSubscription(**kwargs)
        self.list_card_sub.append(card_sub)
        self.container.add_widget(card_sub)










