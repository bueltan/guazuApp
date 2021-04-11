import asyncio
import logging
import uuid

from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport

from connection_endpoint import variables
from database import base
from database.model_messages import ModelMessages
from database.model_message_temp import ModelMessagesTemp
from database.model_tickets import ModelTickets
from general_functions import functions


class NewMessage(object):
    """ user_received and subscription_id don't be none"""
    def __init__(self, subscription_id=None,
                 tickets_id='new_ticket',
                 user_received=None,
                 user_sent=None,
                 main_class=None,
                 father_class=None):

        self.subscription_id = subscription_id
        self.tickets_id = tickets_id
        self.ticket_id_encode = functions.encode('Tickets:'+tickets_id)
        self.user_received = user_received
        self.user_sent = user_sent
        self.session = base.Session()
        self.main_class = main_class
        self.father_class = father_class

    def persistent_message_temp(self, dic_message, id_msg=None):

        if id_msg:
            message_data = ModelMessagesTemp(**dic_message)
            self.session.merge(message_data)
        else:
            dic_message['id'] = str(uuid.uuid4())
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

    def create_message(self, id_msg=None, timestamp=0):
        if id_msg:
            message_temp = ModelMessagesTemp.query.get(id_msg)
            message_temp.timestamp = timestamp
            self.session.merge(message_temp)
            dic_message_temp = message_temp.__dict__.copy()
            del dic_message_temp['_sa_instance_state']
            del dic_message_temp['subscription_id']
            dic_message_temp['id'] = functions.encode('Message:'+str(dic_message_temp['id']))
            dic_message_temp['id_bubble'] = functions.encode('Message:'+str(dic_message_temp['id']))
            logging.warning(f"dic_message_temp: {dic_message_temp}")
            message = ModelMessages(**dic_message_temp)
            self.session.merge(message)
            if self.ticket_id_encode:
                ticket = ModelTickets.query.get(self.ticket_id_encode)
                ticket.last_id_msg = message_temp.id
                ticket.read = True
                self.session.merge(ticket)
            self.session.commit()
            asyncio.create_task(self.sent_message(message=message, ticket=ticket, id_message_temp=id_msg))
        return message, ticket

    async def sent_message(self, message=None, ticket=None, id_message_temp=None):
        account_id = self.main_class.account.id
        try:
            transport = AIOHTTPTransport(url=variables.base_url_http,  headers=variables.headers)
            async with Client(transport=transport, fetch_schema_from_transport=False, execute_timeout=None) as session:
                if not 'Authorization' in variables.headers:
                    raise Exception('Not Authorization, waiting validation')
                query = gql(
                    """
                        mutation ($id_account: ID!, $id_subscription: ID!,
                                        $id_ticket: ID, $id_bubble: String! , $node4: String!,
                                        $type: String!, $text:String, $url: String, 
                                        $mime: String, $caption: String, $filename: String,
                                        $vcardList: String, $payload:String ) {
                          CreateMessage(
                            id_account:$id_account
                            id_subscription:$id_subscription
                            id_bubble: $id_bubble
                            ticket_data: { node4: $node4
                                           id: $id_ticket
                                            }
                            message_data: {
                            type: $type
                            text: $text
                            url: $url
                            mime: $mime
                            caption: $caption
                            filename: $filename
                            vcardList: $vcardList
                            payload: $payload
                            }) 
                            {
                            message {
                              id
                            }
                          }
                        }
                    """
                )

                message_params = {'type': message.type,
                                  'text': message.text,
                                  'url': message.url,
                                  'mime': message.mime,
                                  'caption': message.caption,
                                  'filename': message.filename,
                                  'vcardList': message.vcardList,
                                  'payload': message.payload}

                params = {'id_account': account_id, 'id_subscription': ticket.subscription_id,
                          'id_ticket': ticket.id, 'id_bubble': message.id, 'node4': self.user_received}

                params.update(message_params)

                result = await session.execute(query, variable_values=params)
                logging.info(f"sent message to server, {result}")
                self.delete_temp_message(id_message=id_message_temp)

        except Exception as e:
            logging.exception(f"Sent message exeption {e}")
            if 'Not Authorization, waiting validation' in str(e)\
                    or 'Cannot connect to host entity.ar' in str(e):
                await self.main_class.check_connection()

    def delete_temp_message(self, id_message=None):
        logging.info(f'delete_temp_message new_id : {id_message} ')
        try:
            if id_message:
                ModelMessagesTemp.query.filter(ModelMessagesTemp.id == id_message).delete()
                self.session.commit()
        except Exception as e:
            logging.exception(f"delete_temp_message {e}")
