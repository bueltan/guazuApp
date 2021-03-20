import asyncio
import backoff
from gql import Client
from gql.transport.websockets import WebsocketsTransport


@backoff.on_exception(backoff.expo, Exception, max_time=300)


async def graphql_websocket_connection():
    transport = WebsocketsTransport(url="wss://YOUR_URL")
    client = Client(transport=transport, fetch_schema_from_transport=True)

    async with client as session:
        task4 = asyncio.create_task(execute_subscription2(session))
        await asyncio.gather(task1, task2, task3, task4)
