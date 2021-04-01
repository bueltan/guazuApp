import ast
import asyncio
import logging
from gql import Client, gql
from gql.transport.websockets import WebsocketsTransport
from connection_endpoint import variables
from database import base
from database.model_messages import ModelMessages
from database.model_tickets import ModelTickets
from general_functions import functions
logging.getLogger('backoff').addHandler(logging.StreamHandler())


class TunnelSubscriptions(object):
    def __init__(self, MainClass):
        self.sessionSQL = base.Session()
        self.work_queue = asyncio.Queue()

        self.subscription_id = None
        self.main_class = MainClass

    async def tunnel_subscriptions(self, subscription_id=None, timestamp=0):
        self.subscription_id = subscription_id
        logging.info(f"tunnel_subscriptions subscription_id: {subscription_id}, timestamp: {timestamp} ")

        query = gql("""subscription($subscription_id: ID! $timestamp:Int!)
        {subscribe_to_tickets(subscription_id: $subscription_id timestamp: $timestamp)}""")

        parameters = {'subscription_id': self.subscription_id, 'timestamp': timestamp}
        function_name = 'tunnel_subscriptions'
        await self.graphql_connection(query=query, parameters=parameters, function_name=function_name)

    async def graphql_connection(self, **kwargs):
        logging.info("subscription graphql_connection %s", kwargs)
        task_producer = [asyncio.create_task(self.producer(**kwargs))]
        asyncio.create_task(self.subscribe())
        await asyncio.gather(*task_producer, return_exceptions=False)

    async def producer(self, **kwargs):
        payload = {}
        for key, value in kwargs.items():
            payload[key] = value
        logging.info('producer %s', payload)
        await self.work_queue.put(payload)

    def give_up_exception(give_up_exeption):
        if 'connection closed abnormally [internal]' in str(give_up_exeption):
            logging.warning("Lost connection with the server %s", str(give_up_exeption))

    # @backoff.on_exception(backoff.expo, Exception, max_time=None, giveup=give_up_exception)
    async def subscribe(self):
        transport = WebsocketsTransport(url=variables.base_url_ws)
        client = Client(transport=transport)
        try:
            async with client as session:
                payload = await self.work_queue.get()
                logging.info('Tunnel subscribe payload %s', payload)
                async for result in session.subscribe(payload['query'], variable_values=payload['parameters']):
                    if payload['function_name'] == 'tunnel_subscriptions':
                        models = self.build_models(result)
                        new_msg = self.merge_models_db(models)
                        if new_msg:
                            self.update_interfaces(id_tk=models[0].id, messages=models[1])
        except Exception as excep:
            logging.error(f"WebsocketsTransport: {excep}")
            await self.main_class.check_connection()

    def build_models(self, result):
        ticket = None
        message = None
        try:
            payload = ast.literal_eval(result['subscribe_to_tickets'])
            msg_dict = payload.pop('message')
            tk_dict = {}
            list_keys = ['id', 'subscription_id', 'user_id', 'channel_id',
                         'node2', 'node3', 'node4', 'phone', 'name', 'image',
                         'count', 'last_id_msg', 'read', 'timestamp']

            for k, v in payload.items():
                if k in list_keys:
                    tk_dict[k] = v
            tk_dict['subscription_id'] = self.subscription_id
            msg_dict['id'] = functions.encode('Message:' + str(msg_dict['id']))
            tk_dict['id'] = functions.encode('Tickets:' + str(tk_dict['id']))
            tk_dict['read'] = False
            ticket = ModelTickets(**tk_dict)
            message = ModelMessages(**msg_dict)

        except Exception as error:
            logging.error(f'give_up_exeption in build_models :{error}')

        return ticket, message

    def merge_models_db(self, models):
        tickets = models[0]
        messages = models[1]
        new_msg = True
        if tickets and messages:
            try:
                check = ModelMessages.query.get(messages.id)
                if check:
                    logging.info("current message exist in db ID: %s", messages.id)
                    new_msg = False
                else:
                    logging.info("Is new message ID: %s", messages.id)
                    self.sessionSQL.merge(tickets)
                    self.sessionSQL.add(messages)
                    self.sessionSQL.commit()
                    new_msg = True
            except Exception as error:
                self.sessionSQL.rollback()
                new_msg = False
                logging.error(f'give_up_exeption in merge_models_db :{error}')
            finally:
                return new_msg

    def update_interfaces(self, id_tk=None, messages=None):
        self.main_class.class_update_interface. \
            mutate_ticket(model_msgs=messages, subscription_id=self.subscription_id, ticket_id=id_tk)
        self.main_class.class_update_interface.update_current(subscription_id=self.subscription_id,
                                                              id_tk_encode=id_tk, message_obj=messages)