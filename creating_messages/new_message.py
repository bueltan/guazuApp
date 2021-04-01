import logging

from database import  base
from database.model_messages import ModelMessages
from database.model_message_temp import ModelMessagesTemp
from database.model_tickets import ModelTickets
from general_functions import functions


class NewMessage(object):
    """ user_received and subscription_id don't be none"""
    def __init__(self, subscription_id=None,
                 tickets_id='new_ticket',
                 user_received=None,
                 user_sent=None):
        self.subscription_id = subscription_id
        self.tickets_id = tickets_id
        self.ticket_id_encode = functions.encode('Tickets:'+tickets_id)
        self.user_received = user_received
        self.user_sent = user_sent
        self.session = base.Session()

    def persistent_message_temp(self, dic_message, id_msg=None):
        if id_msg:
            message_data = ModelMessagesTemp(**dic_message)
            self.session.merge(message_data)
        else:
            dic_message['subscription_id'] = self.subscription_id
            dic_message['tickets_id'] = self.tickets_id
            dic_message['user_received'] = self.user_received
            dic_message['user_sent'] = self.user_sent
            message_data = ModelMessagesTemp(**dic_message)
            self.session.add(message_data)
            id_msg = message_data.id
        self.session.commit()
        logging.info(f"persistent_message_temp: {id_msg}" )
        return message_data.id

    def remove_message_temp(self, **kwargs):
        pass

    def sent_message_temp(self, id_msg=None, timestamp=0):
        if id_msg:
            message_temp = ModelMessagesTemp.query.get(id_msg)
            message_temp.timestamp = timestamp
            self.session.merge(message_temp)
            dic_message_temp = message_temp.__dict__.copy()
            del dic_message_temp['_sa_instance_state']
            del dic_message_temp['subscription_id']
            dic_message_temp['id'] = functions.encode('Message:'+str(dic_message_temp['id']))
            logging.warning(f"dic_message_temp: {dic_message_temp}")
            copy_to_message = ModelMessages(**dic_message_temp)
            self.session.merge(copy_to_message)
            if self.ticket_id_encode:
                ticket = ModelTickets.query.get(self.ticket_id_encode)
                ticket.last_id_msg = message_temp.id
                ticket.read = True
                self.session.merge(ticket)
            self.session.commit()
        return copy_to_message, ticket
