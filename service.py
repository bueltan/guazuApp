import ast
import asyncio
import base64
import logging
import time
from gql import Client, gql
from gql.transport.websockets import WebsocketsTransport
from connection_endpoint import variables
from database import base
from database.model_account import ModelAccount
from database.model_messages import ModelMessages
from database.model_subscription import ModelSubscriptions
from database.model_tickets import ModelTickets
from general_functions import functions
from pythonosc.osc_server import AsyncIOOSCUDPServer
from pythonosc.dispatcher import Dispatcher
from validation_account_service import validate_account
from pythonosc.udp_client import SimpleUDPClient


class TunnelSubscriptions(object):

    def __init__(self):
        self.sessionSQL = base.Session()
        self.work_queue = asyncio.Queue()
        self.subscription_id = None
        self.dispatcher = Dispatcher()
        self.dispatcher.map("/filter_service*", self.filter_handler)
        self.account = None
        self.client = SimpleUDPClient("127.0.0.1", 8542)  # Create client
        self.client.send_message("/filter_interface/notifications",
                                 ["start service tunnel subscriptions"])  # Send message with int, float and string

    async def open_tunnel(self, subscription_id=None, timestamp=0):
        self.account = self.sessionSQL.query(ModelAccount).filter_by(current=1, keepOpen=True).first()

        if self.account:
            subscriptions = ModelSubscriptions.query.filter_by(id_account=functions.decode(self.account.id))
            if subscription_id is None:
                for subscription in subscriptions:
                    await self.tunnel_subscriptions(subscription_id=subscription.id,
                                                    timestamp=subscription.last_sync_timestamp)
            else:
                await self.tunnel_subscriptions(subscription_id=subscription_id, timestamp=timestamp)

    async def tunnel_subscriptions(self, subscription_id=None, timestamp=0):
        print(f"tunnel_subscriptions {subscription_id} timestamp {timestamp}")
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

    async def subscribe(self):
        transport = WebsocketsTransport(url=variables.base_url_ws, headers=variables.headers)
        client = Client(transport=transport)
        try:
            if not 'Authorization' in variables.headers:
                raise Exception('Not Authorization, waiting validation')
            async with client as session:
                payload = await self.work_queue.get()
                logging.info('Tunnel subscribe success payload %s', payload)
                async for result in session.subscribe(payload['query'], variable_values=payload['parameters']):
                    if payload['function_name'] == 'tunnel_subscriptions':
                        logging.info(f"tunnel_subscriptions data :{result}")
                        models = self.build_models(result)
                        models_tk_msg = self.merge_models_db(models)
                        if models_tk_msg[2]:
                            listModel = [i for i in models_tk_msg[i]]
                            print(type(listModel))
                            self.client.send_message("/filter_interface/update_interface",
                                                     [models_tk_msg[0].id])

        except Exception as e:
            logging.warning(f"WebsocketsTransport: {e}")
            if 'connection closed abnormally [internal]' in str(e):
                variables.headers.pop('Authorization')
                logging.warning(e)
                await self.subscribe()
            if 'Not Authorization, waiting validation' in str(e):
                logging.warning(f"WebsocketsTransport: try again in 1 second")
                await asyncio.sleep(1)
                password_decode = base64.b85decode(self.account.password).decode("utf-8")
                await validate_account(password_decode, self.account.id_name)
                await self.subscribe()

    def update_timestamp_subscription(self, new_timestamp=None):
        subscription = ModelSubscriptions.query.get(self.subscription_id)
        try:
            if not subscription:
                raise Exception('subscription not found')
            else:
                timestamp_in_db = subscription.last_sync_timestamp
                if timestamp_in_db is not None:
                    if new_timestamp > timestamp_in_db:
                        diff_time = new_timestamp - timestamp_in_db
                        if diff_time <= 300:
                            subscription.last_sync_timestamp = new_timestamp
                            self.sessionSQL.merge(subscription)
                            self.sessionSQL.commit()
                            logging.info(f"update_timestamp_subscription in db {new_timestamp}")
                        else:
                            logging.info(f"update_timestamp_subscription too much time diff , call sync ")

                            self.client.send_message("/filter_interface/notifications",
                                                     ["start service tunnel subscriptions"])

                            """
                            self.main_class.class_sync_data.sync_tickets(id_subscription=self.subscription_id,
                                                                         timestamp=timestamp_in_db)"""
        except Exception as e:
            logging.warning(f"update_timestamp_subscription: {e}")

    def build_models(self, result):
        ticket = None
        message = None
        try:
            payload = ast.literal_eval(result['subscribe_to_tickets'])
            print(payload)
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

        except Exception as e:
            logging.error(f'give_up_exeption in build_models :{e}')

        return ticket, message

    def merge_models_db(self, models):

        tickets = models[0]
        messages = models[1]
        new_msg = True
        if tickets and messages:
            try:
                if messages.user_sent == self.account.id_name:
                    logging.warning("this message come from me ")
                    updated_message = self.replace_message_in_db(old_id=messages.id_bubble, new_id=messages.id)
                    if updated_message is not None:
                        messages = updated_message
                    else:
                        tickets.read = True
                        messages.success = True
                        self.sessionSQL.merge(tickets)
                        self.sessionSQL.add(messages)
                        self.sessionSQL.commit()
                        new_msg = True
                else:
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
            except Exception as e:
                self.sessionSQL.rollback()
                new_msg = False
                logging.error(f'Tunnel subscriptions merge_models_db :{e}')
            finally:
                self.update_timestamp_subscription(int(time.time()))
                return tickets, messages, new_msg

    def replace_message_in_db(self, old_id=None, new_id=None):
        logging.warning(f'replace_message_in_db new_id : {new_id} ')
        if new_id:
            logging.warning(f"replace_message_in_db old_id : {old_id}")
            temp_message = ModelMessages.query.get(old_id)
        if temp_message is None:
            print("temp_message is None")
            return None
        ModelMessages.query.filter(ModelMessages.id == temp_message.id).delete()
        new_message = temp_message
        new_message.id = new_id
        new_message.success = True
        self.sessionSQL.merge(new_message)
        self.sessionSQL.commit()
        self.sessionSQL.close()
        return new_message

    def filter_handler(self, address, *args):
        method = address.split("/")[2]
        if method == 'subscribe':
            print(method, args)

    async def init_main(self):
        server = AsyncIOOSCUDPServer(("127.0.0.1", 8544), self.dispatcher, asyncio.get_event_loop())
        await server.create_serve_endpoint()  # Create datagram endpoint and start serving
        await self.open_tunnel()  # Enter main loop of program


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    asyncio.ensure_future(TunnelSubscriptions().init_main())
    loop.run_forever()