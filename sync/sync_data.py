import time

import backoff
from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport
from connection_endpoint import variables
from sync.sync_subscriptions import SyncSubscriptions
from sync.sync_tickets import SyncTickets
from database import base

from sync.sync_messages import SyncMessages
import asyncio
import logging
logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')


class SyncData(object):
    def __init__(self, MainClass):
        self.sessionSQL = base.Session()
        self.work_queue = asyncio.Queue()
        self.account_id = None
        self.main_class = MainClass

    async def graphql_connection(self, **kwargs):
        logging.info("graphql_connection %s", kwargs)
        task_producer = [asyncio.create_task(self.producer(**kwargs))]
        asyncio.gather(*task_producer, return_exceptions=True)
        asyncio.create_task(self.execute())

    async def producer(self, **kwargs):
        payload = {}
        for key, value in kwargs.items():
            payload[key] = value
        logging.info('producer %s', payload)
        await self.work_queue.put(payload)

    def give_up_exception(ext):
        if 'Not Authorization' in str(ext):
            logging.warning(f" In backoff sync_data {str(ext)}")
        else:
            logging.error(f" In backoff sync_data {str(ext)}")

    @backoff.on_exception(backoff.expo, Exception, max_tries= None, giveup=give_up_exception)
    async def execute(self):

        transport = AIOHTTPTransport(url=variables.base_url_http, headers=variables.headers, timeout=100)
        client = Client(transport=transport, fetch_schema_from_transport=False, execute_timeout=100)
        if not  'Authorization' in variables.headers:
            raise Exception('Not Authorization, waiting validation')
        async with client as session:
            payload = await self.work_queue.get()
            spread_sync = payload['spread_sync'] - 1
            logging.info("to execute parameters %s and query %s", payload['parameters'], payload['query'])
            result = await session.execute(payload['query'], variable_values=payload['parameters'])

            """ Result subscribe Sync subscriptions """

            if payload['function'] == 'sync_subscriptions':
                account = payload['account']
                list_obj_subscriptions = await SyncSubscriptions(MainClass=self.main_class, account_obj=account,
                                                                 session=self.sessionSQL).success(result)

                logging.info('sync_subscriptions %s', list_obj_subscriptions)
                if spread_sync >= 0:
                    for obj_subs in list_obj_subscriptions:
                        await self.sync_tickets(spread_sync, obj_subs.id, obj_subs.last_sync_timestamp)
                else:
                    self.sessionSQL.commit()
                    self.sessionSQL.close()

            """ Result subscribe Sync tickets """

            if payload['function'] == 'sync_tickets':
                logging.info("Result subscribe Sync tickets'")
                id_subscription = payload['id_subscriptions']
                current_time = int(time.time())

                """ update timestamp last sync """

                if len(result['get_tickets']['edges']) > 0:
                    list_obj_tickets = SyncTickets(subscription_id=id_subscription,
                                                   MainClass=self.main_class,
                                                   timestamp=payload['timestamp'],
                                                   session=self.sessionSQL).success(result)

                    if spread_sync >= 0:
                        logging.info("SyncSubscriptions-update_timestamp_sync_subs")

                        logging.info("Result subscribe Sync tickets spread_sync >= 0 get messages tk a tk %s",
                                     payload['timestamp'])

                        for obj_tks in list_obj_tickets:
                            await self.sync_messages(id_ticket=obj_tks.id,
                                                     timestamp=payload['timestamp'],
                                                     spread_sync=spread_sync,
                                                     id_subscription=id_subscription)

                        SyncSubscriptions(account_id=self.account_id, session=self.sessionSQL). \
                            update_timestamp_sync_subs(current_time, id_subscription)
                        self.sessionSQL.commit()
                    else:
                        logging.info("SyncSubscriptions-update_timestamp_sync_subs")
                        SyncSubscriptions(account_id=self.account_id, session=self.sessionSQL). \
                            update_timestamp_sync_subs(current_time, id_subscription)
                        self.sessionSQL.commit()
                        self.sessionSQL.close()

                else:
                    logging.info("SyncSubscriptions-update_timestamp_sync_subs")
                    SyncSubscriptions(account_id=self.account_id, session=self.sessionSQL). \
                        update_timestamp_sync_subs(current_time, id_subscription)
                    self.sessionSQL.commit()
                    self.sessionSQL.close()

            """ Result subscribe Sync messages """

            if payload['function'] == 'sync_messages':
                logging.info('Result subscribe Sync messages sync_messages %s', result)
                SyncMessages(ticket_id=payload['id_ticket'],
                             MainClass=self.main_class,
                             timestamp=payload['timestamp'],
                             id_subscription=payload['id_subscription'],
                             session=self.sessionSQL).success(result)

                if spread_sync >= 0:
                    logging.info("Result subscribe Sync messages, download Multimedia msg")

        self.work_queue.task_done()
        """" Sync Subscription """

    async def sync_subscriptions(self, account, spread_sync=0):
        self.account_id = account.id
        logging.info("Sync Subscription Build Query, spread_sync: %s", spread_sync)
        query = gql(""" 
                query ($id_account: ID! ){subscription_list(id_account:$id_account){edges {node {id source id_account}}}}""")

        parameters = {'id_account': self.account_id}
        function = 'sync_subscriptions'
        await self.graphql_connection(function=function, query=query, parameters=parameters,
                                      spread_sync=spread_sync, account=account)

    """" Sync Tickets """

    async def sync_tickets(self, spread_sync, id_subscription=None, timestamp=0):
        logging.info("Sync Tickets Build Query, timestamp: %s", timestamp)
        timestamp = timestamp
        if timestamp == 0:
            query = gql(""" 
                      query ($id_subscription:ID! $timestamp:String!)
                      {get_tickets(id_subscription: $id_subscription timestamp: $timestamp)
                                          {edges{ node {id, user_id, channel_id, node2, node3,
                                          node4, name, timestamp, image, phone, last_id_msg  
                                          listMessage{edges{node{ 
                                          id tickets_id type text fromMe 
                                          mime url caption filename payload 
                                          vcardList timestamp user_sent user_received }}}}}}}
                          """)
            spread_sync = 0

        else:
            query = gql(""" 
                      query ($id_subscription:ID! $timestamp:String!)
                      {get_tickets(id_subscription: $id_subscription timestamp: $timestamp)
                                          {edges{ node {id, user_id, channel_id, node2, node3,
                                          node4, name, timestamp, image, phone, last_id_msg 
                                          }}}}
                          """)

        parameters = {'id_subscription': id_subscription, 'timestamp': timestamp}

        function = 'sync_tickets'

        await self.graphql_connection(function=function, query=query,
                                      parameters=parameters, timestamp=timestamp,
                                      id_subscriptions=id_subscription, spread_sync=spread_sync)

    """" Sync Messages """

    async def sync_messages(self, id_ticket=None, timestamp=0, spread_sync=0, id_subscription=None):

        logging.info(f"Sync Messages Build Query id_tk {id_ticket}, timestamp{timestamp}:")

        query = gql(""" 
                       query ($id_ticket: ID! $timestamp: Int!) {list_message (tickets_id: $id_ticket,
                                                                               timestamp:$timestamp)
                       {edges{node {id tickets_id type text fromMe 
                                             mime url caption filename payload 
                                             vcardList timestamp  user_sent user_received } } } }
                       """)

        parameters = {'id_ticket': id_ticket, 'timestamp': timestamp}

        function = 'sync_messages'
        await self.graphql_connection(function=function, query=query,
                                      parameters=parameters, timestamp=timestamp,
                                      id_ticket=id_ticket, spread_sync=spread_sync,
                                      id_subscription=id_subscription)

    async def sync_sent_messages_pending(self, id_ticket=None, timestamp_queue=0, spread_sync=0, id_subscription=None):

        logging.info(f"sync_sent_messages_pending {id_ticket}, timestamp{timestamp_queue}:")

        query = gql(""" 
                       
                       """)

        parameters = {'id_ticket': id_ticket, 'timestamp_queue': timestamp_queue}

        function = 'sync_messages'
        await self.graphql_connection(function=function, query=query,
                                      parameters=parameters, timestamp=timestamp_queue,
                                      id_ticket=id_ticket, spread_sync=spread_sync,
                                      id_subscription=id_subscription)