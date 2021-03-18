import asyncio
import base64
import hashlib

import backoff
from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.snackbar import Snackbar
from database.model_account import ModelAccount
from database import base
from connection_endpoint import variables


class Login(MDBoxLayout):
    def __init__(self, mainwid, **kwargs):
        super(Login, self).__init__()
        self.session = base.Session()
        self.mainwid = mainwid
        self.keepOpen.on_release = lambda: self.change_ck()
        self.ck_keepOpen.on_release = lambda: self.stop_task_validate()
        self.id_name = None
        self.password = None
        self.validate_task = None

        #self.data_login = {'my_id': '', 'my_id_account_name': ''}

    def stop_task_validate(self):
       if self.ck_keepOpen.active == False:
            if self.validate_task is not None:
                self.validate_task.cancel()

    def change_ck(self):
        if not self.ck_keepOpen.active:
            self.ck_keepOpen.active = True
        else:
            self.ck_keepOpen.active = False
            self.stop_task_validate()

    def create_task_validate_account(self):
        if self.validate_task == None:
            self.validate_task = asyncio.create_task(self.validate_account(), name="validate_account")
        else:
           self.validate_task.cancel()
           self.validate_task = asyncio.create_task(self.validate_account(), name="validate_account")

    def fatal_code(e):
        print("fatal_code", e)
        if 'Authenication Failure' in str(e):
            Snackbar(text="Usuario o contraseña incorrecto", padding="20dp").open()
            return 400
        if 'Temporary failure in name resolution' in str(e):
            Snackbar(text="No se puede establecer connexion con el servidor", padding="20dp").open()

    @backoff.on_exception(backoff.expo, Exception, max_time=300, giveup=fatal_code)
    async def validate_account(self):
        transport = AIOHTTPTransport(url=variables.base_url_http)
        async with Client(transport=transport, fetch_schema_from_transport=True) as session:
            password = (hashlib.md5(self.password.encode('utf-8')).hexdigest())
            print(password, "--", self.password)
            query = gql(
                """mutation($id_name: String! $password: String! ){validateAccount
                (id_name: $id_name  
                password:$password)
                {access_token, refresh_token, id_account }}"""
                )
            params = {'id_name': self.id_name, 'password': password}

            result = await session.execute(query, variable_values=params)
            await self.success(result)

    async def success(self, results):
        self.validate_task = None
        account = ModelAccount()
        account.id = results['validateAccount']['id_account']
        account.id_name = self.id_name
        account.keepOpen = self.ck_keepOpen.active
        password = base64.b85encode(self.password.encode("utf-8"))
        account.password = password
        variables.headers.update({'Authorization': 'Bearer '+results['validateAccount']['access_token']})
        print(variables.headers)
        await self.mainwid.goto_mainNavigation(id=account.id, id_name=password)




    def go_in(self):
        # DELETE THIS DON'T FORGET
        self.id_name = "." + self.user_input.text.lower()
        self.password = self.password_input.text
        self.create_task_validate_account()

    def go_to_register(self):
        self.mainwid.goto_register()

    def save_account(self, data):
        message = ModelAccount(**data)
        self.session.merge(message)
        self.session.commit()
        self.session.close()

    def update_account(self, data):
        self.session.merge(data)
        self.session.commit()
        self.session.close()

    def load_account_from_db(self):
        account = self.session.query(ModelAccount).filter_by(current=1).first()
        try:
            if account.keepOpen:
                self.ck_keepOpen.active = account.keepOpen
                self.user_input.text = account.id_name.split(".")[1]
                self.password_input.text = base64.b85decode(account.password).decode("utf-8")
                self.go_in()

        except:
            pass
        self.session.close()

    def save_image_account(id):
        pass
