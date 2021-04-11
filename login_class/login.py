import asyncio
import base64
import hashlib
import logging

import backoff
from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.snackbar import Snackbar

from connection_endpoint import variables
from database import base
from database.model_account import ModelAccount
from general_functions import functions

logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')


class Login(MDBoxLayout):
    def __init__(self, mainwid):
        super(Login, self).__init__()
        self.session = base.Session()
        self.mainwid = mainwid
        self.id_name = None
        self.password = None
        self.account = None
        self.keep_open = False

    def change_ck(self):
        if not self.ck_keepOpen.active:
            self.ck_keepOpen.active = True
        else:
            self.ck_keepOpen.active = False

    async def create_tasks(self,):
        task1 = asyncio.create_task(self.validate_account())
        task2 = asyncio.create_task(self.after_gate())
        await asyncio.gather(task1, task2)

    async def after_gate(self):
        logging.debug("after_gate")
        if self.account:
            await self.mainwid.goto_main_navigation(account=self.account)

    def fatal_code(e):
        logging.warning(e)
        if 'Authenication Failure' in str(e):
            Snackbar(text="Usuario o contraseña incorrecto", padding="20dp").open()
            return 400
        if 'Temporary failure in name resolution' in str(e):
            #Snackbar(text="Sin connexion a internet", padding="20dp").open()
            logging.warning("Sin connexion a internet")
        if 'Cannot connect to host' in str(e):
            #Snackbar(text="No se puede establecer connexion con el servidor", padding="20dp").open()
            logging.warning("No se puede establecer connexion con el servidor")
        else:
            return 400

    @backoff.on_exception(backoff.constant, Exception, interval=10, max_tries=None, giveup=fatal_code)
    async def validate_account(self, waiting_validation=None, reload=None):
        transport = AIOHTTPTransport(url=variables.base_url_http)
        password = hashlib.md5(self.password.encode('utf-8')).hexdigest()
        print(password, "--", self.password)
        async with Client(transport=transport, fetch_schema_from_transport=False, execute_timeout=None) as session:

            query = gql(
                """mutation($id_name: String! $password: String! ){validateAccount
                (id_name: $id_name  
                password:$password)
                {access_token, refresh_token, id_account }}"""
                )
            params = {'id_name': self.id_name, 'password': password}
            result = await session.execute(query, variable_values=params)
            id_account = functions.decode(result['validateAccount']['id_account'])
            id_account = functions.encode('Account:'+id_account)
            query = gql(
                """ query($id:ID! ){account(id:$id)
                {id id_name name email profile_img }} """
            )
            params = {'id': id_account}
            data_account = await session.execute(query, variable_values=params)
            self.set_data_account(data_account)
            await self.success(result, after_gate=waiting_validation, reload=reload)
            return result

    def on_checkbox_active(self, checkbox, value):
        if value:
            self.keep_open = True
            self.change_autologin(True)
        else:
            self.keep_open = False
            self.change_autologin(False)

    def set_data_account(self, data_account):
        logging.info("set_data_account")
        data_account = data_account['account']
        data_account['keepOpen'] = self.keep_open
        data_account['current'] = True
        data_account['password'] = base64.b85encode(self.password_input.text.encode("utf-8"))
        self.change_state_current_accounts()
        self.persistent_account(data_account)
        self.account = self.session.query(ModelAccount).filter_by(id=data_account['id']).first()

    async def success(self, results, after_gate=None, reload=None):
        self.validate_task = None
        access_token = results['validateAccount']['access_token']
        variables.headers.update({'Authorization': 'Bearer '+access_token})
        logging.info(f"token : {access_token} id_account: {self.account.id}")
        if after_gate is not None:
            asyncio.create_task(self.after_gate())
        if reload:
            await self.mainwid.class_sync_data.sync_subscriptions(self.account, 3)
            self.mainwid.checking = False

    def go_in(self, account=None):
        logging.info(f"go_in account :{account} ")
        event_loop = asyncio.get_event_loop()
        logging.info("go_in ")
        if not account:
            logging.info("go_in not account")
            self.id_name = "." + self.user_input.text.lower()
            self.password = self.password_input.text
        else:
            self.account = account
            self.id_name = self.account.id_name
            self.password = self.account.password
            self.user_input.text = self.account.id_name
            self.password_input.text = self.account.password
            logging.info(f"go_in from register id_name {self.id_name}, password: {self.password}")
        asyncio.ensure_future(self.create_tasks(), loop=event_loop)

    def go_to_register(self):
        self.mainwid.goto_register()

    def change_state_current_accounts(self):
        logging.info("change_state_current_accounts")
        accounts = self.session.query(ModelAccount)
        try:
            if accounts[0]:
                for account in accounts:
                    account.current = 0
                    self.session.merge(account)
        except Exception as e:
            logging.error(f"change_state_current_accounts: {e} ")

    def change_autologin(self, value):
        if self.account:
            if '.' + self.user_input.text == self.account.id_name:
                self.account.keepOpen = value
                self.session.merge(self.account)
                self.session.commit()
                self.session.close()

    def persistent_account(self, data):
        account = ModelAccount(**data)
        self.session.merge(account)
        self.session.commit()
        self.session.close()

    def load_account_from_db(self):
        self.account = self.session.query(ModelAccount).filter_by(current=1).first()
        try:
            logging.info(f" load_account_from_db .id_name : {self.account.id_name}")
            self.ck_keepOpen.active = self.account.keepOpen
            self.user_input.text = self.account.id_name.split(".")[1]
            self.password_input.text = base64.b85decode(self.account.password).decode("utf-8")
            if self.account.keepOpen:
                    self.go_in()
        except Exception:
            logging.info("Database without accounts registered")
        self.session.close()
        return self.account

    def validate_local(self):
        self.id_name = "." + self.user_input.text.lower()
        self.password = self.password_input.text
        logging.info(f"validate_local: self.id_name: {self.id_name}, self.password: {self.password}")
        check = ModelAccount.query.filter_by(id_name=self.id_name).first()
        try:
            if check:
                if base64.b85decode(check.password).decode("utf-8") == self.password:
                    self.account = ModelAccount.query.filter_by(id_name=self.id_name).first()
                    self.go_in()
                else:
                    Snackbar(text="Contraseña incorrecta", padding="20dp").open()

            else:
                asyncio.create_task(self.validate_account(waiting_validation=True))

        except Exception as e:
            logging.error(f"validate_local: {e}")

    def save_image_account(self, id):
        pass
