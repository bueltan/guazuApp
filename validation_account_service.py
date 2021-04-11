import hashlib
import logging
import backoff
from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport
from connection_endpoint import variables


@backoff.on_exception(backoff.constant, Exception, interval=10, max_tries=None)
async def validate_account(password, id_name):
    transport = AIOHTTPTransport(url=variables.base_url_http)
    password = hashlib.md5(password.encode('utf-8')).hexdigest()

    async with Client(transport=transport, fetch_schema_from_transport=False, execute_timeout=None) as session:
        query = gql(
            """mutation($id_name: String! $password: String! ){validateAccount
            (id_name: $id_name  
            password:$password)
            {access_token, refresh_token, id_account }}"""
        )
        params = {'id_name': id_name, 'password': password}
        result = await session.execute(query, variable_values=params)
        access_token = result['validateAccount']['access_token']
        variables.headers.update({'Authorization': 'Bearer ' + access_token})
        logging.info(f"token : {access_token}")

