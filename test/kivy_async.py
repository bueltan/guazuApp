'''Example shows the recommended way of how to run Kivy with the Python built
in asyncio event loop as just another async coroutine.
'''
import asyncio
import time

from kivy.lang.builder import Builder
from kivymd.app import MDApp
from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport

kv = '''
BoxLayout:
    orientation: 'vertical'
    BoxLayout:
        ToggleButton:
            id: btn1
            group: 'a'
            text: 'Sleeping'
            allow_no_selection: False
            on_state: if self.state == 'down': label.status = self.text
        ToggleButton:
            id: btn2
            group: 'a'
            text: 'Swimming'
            allow_no_selection: False
            on_state: if self.state == 'down': label.status = self.text
        ToggleButton:
            id: btn3
            group: 'a'
            text: 'Reading'
            allow_no_selection: False
            state: 'down'
            on_state: if self.state == 'down': label.status = self.text
        Button:
            id: btn4
            text: 'Create Async Task'
            on_release: app.create_task()
            
    MDLabel:
        id: label
        status: 'Reading'
        text: 'Beach status is "{}"'.format(self.status)
'''


class AsyncApp(MDApp):

    other_task = None

    def build(self):
        return Builder.load_string(kv)

    def create_task(self):
        for i in range(1000):
            asyncio.create_task(self.sleep_asyncrono())


    def app_func(self):
        self.other_task = asyncio.ensure_future(self.check_connection())

        async def run_wrapper():
            await self.async_run(async_lib='asyncio')
            print('App done')
            self.other_task.cancel()

        return asyncio.gather(run_wrapper(), self.other_task)

    async def sleep_asyncrono(self):
        transport = AIOHTTPTransport(url="https://countries.trevorblades.com/graphql")

        # Using `async with` on the client will start a connection on the transport
        # and provide a `session` variable to execute queries on this connection
        async with Client(
                transport=transport, fetch_schema_from_transport=True,
        ) as session:
            # Execute single query
            query = gql(
                """
                query getContinents {
                  continents {
                    code
                    name
                  }
                }
            """
            )

            result = await session.execute(query)
            print(result)

    async def check_connection(self):
        try:
            await asyncio.sleep(2)
        except asyncio.CancelledError as e:
            print('Wasting time was canceled', e)
        finally:
            # when canceled, print that it finished
            print('Done wasting time')


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(AsyncApp().app_func())
    loop.close()