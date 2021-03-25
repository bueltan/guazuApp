import ast
import asyncio
import logging
import backoff
from gql import Client, gql
from gql.transport.websockets import WebsocketsTransport
from connection_endpoint import variables
from database import base
from database.model_messages import ModelMessages
from database.model_tickets import ModelTickets
from general_functions import functions


class TunnelSubscriptions(object):
    def __init__(self, MainClass):
        self.sessionSQL = base.Session()
        self.work_queue = asyncio.PriorityQueue()
        transport = WebsocketsTransport(url=variables.base_url_ws)
        self.client = Client(transport=transport)
        self.subscription_id = None
        self.main_class = MainClass
        self.ticket = None
        self.message = None

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
        asyncio.gather(*task_producer, return_exceptions=True)

    async def producer(self, **kwargs):
        payload = {}
        for key, value in kwargs.items():
            payload[key] = value
        logging.info('producer %s', payload)
        await self.work_queue.put(payload)

    def error(error):
        logging.error("in backoff exception function subscribe tunnel %s", str(error))

    @backoff.on_exception(backoff.expo, Exception, max_time=5000, max_tries=1000, giveup=error)
    async def subscribe(self):
        async with self.client as session:
            payload = await self.work_queue.get()
            logging.info('Tunnel subscribe payload %s', payload)
            async for result in session.subscribe(payload['query'], variable_values=payload['parameters']):
                if payload['function_name'] == 'tunnel_subscriptions':
                    id_tk = self.build_models(result)
                    new_msg = self.merge_models_db()
                    if new_msg:
                        if id_tk:
                            self.update_interfaces(id_tk)

    def build_models(self, result):
        payload = ast.literal_eval(result['subscribe_to_tickets'])
        msg_dict = payload.pop('message')
        tk_dict = {}
        list_keys = ['id', 'subscription_id', 'user_id', 'channel_id',
                     'node2', 'node3', 'node4', 'phone', 'name', 'image',
                     'count', 'last_id_msg', 'read', 'timestamp']
        for k, v in payload.items():
            if k in list_keys:
                tk_dict[k] = v

        msg_dict['id'] = functions.encode('Message:' + str(msg_dict['id']))
        tk_dict['id'] = functions.encode('Tickets:' + str(tk_dict['id']))
        self.ticket = ModelTickets(**tk_dict)
        self.message = ModelMessages(**msg_dict)
        return self.ticket.id

    def merge_models_db(self):
        new_msg = False
        if self.ticket and self.message:
            try:
                check = ModelMessages.query.get(self.message.id)
                if check:
                    logging.info("current message exist in db ID: %s", self.message.id)
                    new_msg = False
                else:
                    logging.info("Is new message ID: %s", self.message.id)
                    self.sessionSQL.merge(self.ticket)
                    self.sessionSQL.merge(self.message)
                    self.sessionSQL.commit()
                    new_msg = True
            except Exception as error:
                self.sessionSQL.rollback()
                new_msg = False
                logging.error(f'error in merge_models_db :{error}')
            finally:
                self.sessionSQL.close()
                return new_msg

    def update_interfaces(self, id_tk):
        self.main_class.Update_interface.update_ticket_tertiary_msg(subscription_id=self.subscription_id,
                                                                    ticket_id=id_tk, model_msgs= self.message)
