""" MainNavigation """
from kivymd.uix.boxlayout import MDBoxLayout
from general_functions import functions
from main_navigation.card_subscription import CardSubscription
from database.model_subscription import ModelSubscriptions
import logging
logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')


class MainNavigation(MDBoxLayout):
    """ MainNavigation """
    def __init__(self, MainClass, **kwargs):
        super(MainNavigation, self).__init__()
        logging.info("MainNavigation")
        self.list_card_sub = []
        self.main_class = MainClass

    def load_subscriptions_from_db(self, account=None):
        logging.info("load_subscriptions_from_db Account: %s", account)
        if account:
            subscriptions = ModelSubscriptions.query.filter_by(id_account=functions.decode(account.id))
            for subscription in subscriptions:
                logging.info("load_subscriptions_from_db subscription %s", subscription)
                self.build_card_subscription(subscription=subscription, account=account)

    def build_card_subscription(self, **kwargs):
        """ subscription and account object required"""
        card_sub = CardSubscription(self.main_class, **kwargs)
        self.list_card_sub.append(card_sub)
        self.container.add_widget(card_sub)










