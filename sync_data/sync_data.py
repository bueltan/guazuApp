import time
import backoff
from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport
from assets.eval_func_speed import runtime_log
from connection_endpoint import variables
from sync_data.sync_subscriptions import SyncSubscriptions
from sync_data.sync_tickets import SyncTickets
from database import base

from sync_data.sync_messages import SyncMessages
import asyncio
import logging
logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')


class SyncData(object):
    def __init__(self, MainClass):
        self.sessionSQL = base.Session()
        self.work_queue = asyncio.PriorityQueue()
        transport = AIOHTTPTransport(url=variables.base_url_http, headers=variables.headers, timeout=100)
        self.client = Client(transport=transport, fetch_schema_from_transport=True, execute_timeout=100)
        self.account_id = None
        self.main_class = MainClass

    async def graphql_connection(self, **kwargs):
        logging.info("graphql_connection %s", kwargs)
        task_producer = [asyncio.create_task(self.producer(**kwargs))]
        asyncio.create_task(self.execute())
        asyncio.gather(*task_producer, return_exceptions=True)

    async def producer(self, **kwargs):
        payload = {}
        for key, value in kwargs.items():
            payload[key] = value
        logging.info('producer %s', payload)
        await self.work_queue.put(payload)

    def error(error):
        logging.error(str(error))

    #@backoff.on_exception(backoff.expo, Exception, max_time=300, giveup=error)
    async def execute(self):
        payload = await self.work_queue.get()
        logging.info('execute payload %s', payload)
        spread_sync = payload['spread_sync'] - 1
        async with self.client as session:
            logging.info("to execute parameters %s and query %s", payload['parameters'], payload['query'])
            result = await session.execute(payload['query'], variable_values=payload['parameters'])

            """ Result execute Sync subscriptions """

            if payload['function'] == 'sync_subscriptions':
                account = payload['account']
                list_obj_subscriptions = SyncSubscriptions(MainClass=self.main_class, account_obj=account,
                                                           session=self.sessionSQL).success(result)
                logging.info('sync_subscriptions %s', list_obj_subscriptions)
                if spread_sync >= 0:
                    for obj_subs in list_obj_subscriptions:
                        await self.sync_tickets(spread_sync, obj_subs.id, obj_subs.last_sync_timestamp)
                else:
                    self.sessionSQL.commit()
                    self.sessionSQL.close()

            """ Result execute Sync tickets """

            if payload['function'] == 'sync_tickets':
                current_time = int(time.time())
                logging.info('sync_tickets %s', result)
                logging.info('sync_tickets timestamp %s', payload['timestamp'])

                if len(result['get_tickets']['edges']) > 0:
                    id_subscription = payload['id_subscriptions']
                    list_obj_tickets = SyncTickets(subscription_id=id_subscription,
                                                   MainClass=self.main_class,
                                                   timestamp=payload['timestamp'],
                                                   session=self.sessionSQL).success(result)

                    logging.info(' data_tickets %s', list_obj_tickets)

                    """ update timestamp last sync """

                    SyncSubscriptions(account_id=self.account_id, session=self.sessionSQL).\
                        update_timestamp_sync_subs(current_time, id_subscription)
                    logging.info("get messages %s", spread_sync)

                    if spread_sync >= 0:
                        for obj_tks in list_obj_tickets:
                            await self.sync_messages(id_ticket=obj_tks.id,
                                                     timestamp=payload['timestamp'],
                                                     spread_sync=spread_sync,
                                                     id_subscription=id_subscription)
                    else:
                        self.sessionSQL.commit()
                        self.sessionSQL.close()

            """ Result execute Sync messages """

            if payload['function'] == 'sync_messages':
                logging.info('sync_messages %s', result)
                SyncMessages(ticket_id=payload['id_ticket'],
                             MainClass=self.main_class,
                             timestamp=payload['timestamp'],
                             id_subscription=payload['id_subscription'],
                             session=self.sessionSQL).success(result)

                if spread_sync >= 0:
                    logging.info("Download Multimedia msg")
                self.sessionSQL.commit()
                self.sessionSQL.close()

    """" Sync Message """

    async def sync_subscriptions(self, account, spread_sync=0):
        self.account_id = account.id

        logging.info("sync_subscriptions spread_sync: %s", spread_sync)
        query = gql(""" 
                query ($id_account: ID! ){subscription_list (id_account:$id_account)
                           {edges {node {id source id_account}}}}
                   """)

        parameters = {'id_account': self.account_id}
        function = 'sync_subscriptions'
        await self.graphql_connection(function=function, query=query, parameters=parameters,
                                      spread_sync=spread_sync, account=account)

    """" Sync Tickets """

    async def sync_tickets(self, spread_sync, id_subscription=None, timestamp= 0):
        logging.info("sync_tickets spread_sync: %s", spread_sync)
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
                                          vcardList timestamp  }}}}}}}
                          """)
            spread_sync = 0

        else:
            query = gql(""" 
                      query ($id_subscription:ID! $timestamp:String!)
                      {get_tickets(id_subscription: $id_subscription timestamp: $timestamp)
                                          {edges{ node {id, user_id, channel_id, node2, node3,
                                          node4, name, timestamp, image, phone, last_id_msg}}}}
                          """)

        parameters = {'id_subscription': id_subscription, 'timestamp': timestamp }

        function = 'sync_tickets'

        await self.graphql_connection(function=function, query=query,
                                      parameters=parameters, timestamp=timestamp,
                                      id_subscriptions=id_subscription, spread_sync=spread_sync)

    """" Sync Messages """

    async def sync_messages(self, id_ticket=None, timestamp=0, spread_sync=0, id_subscription=None):
        logging.info("sync_messages id_tk: %s:", id_ticket)
        logging.info("sync_messages timestamp: %s:", timestamp)

        query = gql(""" 
                       query ($id_ticket: ID! $timestamp: Int!) {list_message (tickets_id: $id_ticket,
                                                                               timestamp:$timestamp)
                       {edges{node {id tickets_id type text fromMe 
                                             mime url caption filename payload 
                                             vcardList timestamp} } } }
                       """)

        parameters = {'id_ticket': id_ticket, 'timestamp': timestamp}

        function = 'sync_messages'
        await self.graphql_connection(function=function, query=query,
                                      parameters=parameters, timestamp=timestamp,
                                      id_ticket=id_ticket, spread_sync=spread_sync,
                                      id_subscription=id_subscription)
