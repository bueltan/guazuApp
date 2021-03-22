from kivymd.uix.card import MDCard
from main_navigation.conversations_tks import ConversationTks


class CardSubscription(MDCard):
    """CardSubscription """

    def __init__(self, **kwargs):
        super(CardSubscription, self).__init__()
        self.subscription = kwargs.get('subscription')
        self.account = kwargs.get('account')
        self.id = self.subscription.id
        self.Conversations_tks = ConversationTks(self)
        self.update_data_card(source=self.subscription.source, name_account=self.account.name)
        self.Conversations_tks.mutate_list_tickets()

    def update_data_card(self, **kwargs):
        self.subs_route.text = kwargs.get('source')
        self.name_account.text = kwargs.get('name_account')

