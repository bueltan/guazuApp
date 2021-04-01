import asyncio
import base64
import hashlib
from general_functions import functions
import backoff
from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.snackbar import Snackbar
from database.model_account import ModelAccount
from database import base
from connection_endpoint import variables

import logging
logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')


class Login(MDBoxLayout):
    def __init__(self, mainwid, **kwargs):
        super(Login, self).__init__()
        self.session = base.Session()
        self.mainwid = mainwid
        self.keepOpen.on_release = lambda: self.change_ck()
        self.ck_keepOpen.on_release = lambda: self.stop_task_validate()
        self.id_name = None
        self.password = None
        self.account = None
        self.keep_open = False


    def change_ck(self):
        if not self.ck_keepOpen.active:
            self.ck_keepOpen.active = True
        else:
            self.ck_keepOpen.active = False

    def create_tasks(self):
        asyncio.gather(self.validate_account(), self.after_gate())

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
            Snackbar(text="No se puede establecer connexion con el servidor", padding="20dp").open()
        else:
            return 400

    @backoff.on_exception(backoff.expo, Exception, max_time=None, giveup=fatal_code)
    async def validate_account(self):
        transport = AIOHTTPTransport(url=variables.base_url_http)
        async with Client(transport=transport, fetch_schema_from_transport=False, execute_timeout=None) as session:
            password = hashlib.md5(self.password.encode('utf-8')).hexdigest()
            print(password, "--", self.password)

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
            self.success(result)
            return result

    def on_checkbox_active(self, checkbox, value):
        if value:
            self.keep_open = True
            self.change_autologin(True)
        else:
            self.keep_open = False
            self.change_autologin(False)

    def set_data_account(self, data_account):
        data_account = data_account['account']
        data_account['keepOpen'] = self.keep_open
        data_account['current'] = True
        data_account['password'] = base64.b85encode(self.password_input.text.encode("utf-8"))
        self.change_state_current_accounts()
        self.persistent_account(data_account)
        self.account = self.session.query(ModelAccount).filter_by(id=data_account['id']).first()

    def success(self, results):
        self.validate_task = None
        access_token = results['validateAccount']['access_token']
        variables.headers.update({'Authorization': 'Bearer '+access_token})
        logging.info(f"token : {access_token} id_account: {self.account.id}")



    def go_in(self):
        logging.info("go_in")
        self.id_name = "." + self.user_input.text.lower()
        self.password = self.password_input.text
        self.create_tasks()

    def go_to_register(self):
        self.mainwid.goto_register()

    def change_state_current_accounts(self):
        accounts = self.session.query(ModelAccount)
        try:
            if accounts[0]:
                for account in accounts:
                    account.current = 0
                    self.session.merge(account)
        except Exception:
            pass

    def change_autologin(self, value):
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
            self.ck_keepOpen.active = self.account.keepOpen
            self.user_input.text = self.account.id_name.split(".")[1]
            self.password_input.text = base64.b85decode(self.account.password).decode("utf-8")
            if self.account.keepOpen:
                    self.go_in()
        except Exception:
            logging.info("Database without accounts registered")
        self.session.close()
        return self.account

    def save_image_account(self, id):
        pass
