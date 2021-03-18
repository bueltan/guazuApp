import time

import backoff
from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport
from assets.eval_func_speed import runtime_log
from connection_endpoint import variables
from general_functions import functions
from sync_data.sync_subscriptions import SyncSubscriptions
from sync_data.sync_tickets import SyncTickets
import asyncio

import logging
logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')


class SyncData(object):
    def __init__(self, **kwargs):
        self.account_id = kwargs.get('id')
        self.account_id_name = kwargs.get('id_name')
        self.work_queue = asyncio.PriorityQueue()
        transport = AIOHTTPTransport(url=variables.base_url_http, headers=variables.headers, timeout=100)
        self.client = Client(transport=transport, fetch_schema_from_transport=True, execute_timeout=100)

    def error(e):
        logging.error(str(e))

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

    #@backoff.on_exception(backoff.expo, Exception, max_time=300, giveup=error)
    async def execute(self):
        payload = await self.work_queue.get()
        logging.info('execute %s', payload)

        spread_sync = payload['spread_sync'] - 1
        async with self.client as session:
            logging.info("to execute parameters %s", payload['parameters'])
            result = await session.execute(payload['query'], variable_values=payload['parameters'])

            if payload['function'] == 'sync_subscriptions':
                data_subscriptions = SyncSubscriptions(self.account_id).success(result)
                logging.info('sync_subscriptions %s', data_subscriptions)
                if spread_sync >= 0:
                    for subs in data_subscriptions:
                        logging.info('call sync_tickets %s', data_subscriptions)
                        await self.sync_tickets(**subs)

            if payload['function'] == 'sync_tickets':
                logging.info('sync_tickets %s', result)
                if len(result['ticket_list']['edges']) > 0:
                    data_tickets = SyncTickets().success(result)
                    logging.info(' data_tickets %s', data_tickets)

                SyncSubscriptions(self.account_id).update_timestamp_sync_subs(int(time.time()),
                                                                              payload['id_subscriptions'])

    async def sync_subscriptions(self, spread_sync=0):

        query = gql(""" 
                query ($id_account: ID! ){subscription_list (id_account:$id_account)
                           {edges {node {source,id}}}}
                   """)

        parameters = {'id_account': self.account_id}
        function = 'sync_subscriptions'
        await self.graphql_connection(function=function, query=query, parameters=parameters, spread_sync=spread_sync)

    async def sync_tickets(self, node2='',
                           node3='', node4='', last_sync_timestamp=None,
                           id=None, spread_sync=0):
        logging.info("sync_tickets %s", type(node2))
        spread_sync = spread_sync - 1
        query = gql(""" 
                  query ( $node2: String! $node3: String! $node4:String! $timestamp:String!)
                  {ticket_list( node2:$node2 node3:$node3 
                                      node4: $node4
                                      timestamp: $timestamp)
                                      {edges{ node 
                                      {id, user_id, channel_id, node2, node3,
                                      node4, name, timestamp, image, phone, last_id_msg}}}}
                      """)

        parameters = {'node2': node2, 'node3': node3,
                      'node4': node4,
                      'timestamp': last_sync_timestamp}

        function = 'sync_tickets'
        await self.graphql_connection(function=function, query=query,
                                      parameters=parameters, id_subscriptions=id, spread_sync=spread_sync)

