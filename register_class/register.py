import asyncio
import base64
import hashlib
import logging
import backoff as backoff
from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.snackbar import Snackbar
from connection_endpoint import variables
from database import base
from database.model_account import ModelAccount


class Register(MDBoxLayout):
    def __init__(self, mainwid, **kwargs):
        super(Register, self).__init__()
        self.mainwid = mainwid
        self.name.bind(focus=self.on_focus)
        self.user.bind(focus=self.on_focus)
        self.password.bind(focus=self.on_focus)
        self.second_password.bind(focus=self.on_focus)
        self.email.bind(focus=self.on_focus)
        self.session = base.Session()
        self.task_create_account = None
        self.account = None
        self.password_from_field = None

    def create_task_account(self, name, user, password, email):
        logging.info(f"create_task_account, name: {name}, user: {user}, password: {password}, email:{email}" )
        if self.task_create_account == None:
            self.task_create_account = asyncio.create_task(self.create_account(name, user, password, email))
        else:
            self.task_create_account.cancel()
            self.task_create_account = asyncio.create_task(self.create_account(name, user, password, email))

    def fatal_code(e):
        str_error = str(e)
        if 'Duplicate entry' in str_error:
            error_msg = "Ya se encuentra una cuenta con el mismo email o nombre de usuario"
            Snackbar(text=error_msg, padding="20dp").open()
            return 400
        if "for key 'id_name'" in str_error:
            error_msg = "Nombre de cuenta en uso."
            Snackbar(text=error_msg, padding="20dp").open()
            return 400
        if "for key 'email'" in str_error:
            error_msg = "Email ya registrado."
            Snackbar(text=error_msg, padding="20dp").open()
            return 400
        if 'Temporary failure in name resolution' in str(e):
            Snackbar(text="Se ha perdido connexion con internet, reintentando...", padding="20dp").open()
        else:
            logging.error(e)
            return 400

    @backoff.on_exception(backoff.expo, Exception, max_time=300, giveup=fatal_code)
    async def create_account(self, name, user, password, email):

        password = (hashlib.md5(password.encode('utf-8')).hexdigest())
        transport = AIOHTTPTransport(url=variables.base_url_http)

        async with Client(transport=transport, fetch_schema_from_transport=True) as session:
            # Execute single query
            query = gql(
                '''mutation ($name: String!, $id_name: String!, $password:String!, $email:String! ){createAccount (input:{name:$name
                                              id_name:$id_name
                                              password : $password
                                              email: $email })
                                              {account
                                              {name id_name email id code created edited password }}}
                                            '''
            )
            params = {'name': name, 'id_name': user, 'password': password, 'email': email}

            result = await session.execute(query, variable_values=params)
            self.success(result)

    def success(self, results):
        print("success", results)
        if 'errors' in results:
            Snackbar(text=results['errors'][0]['message'], padding="20dp").open()
        else:

            id = results['createAccount']['account']['id']
            name = results['createAccount']['account']['name']
            id_name = results['createAccount']['account']['id_name']
            email = results['createAccount']['account']['email']
            new_account = {'id': id, 'name': name, 'id_name': id_name,
                           'email': email, 'keepOpen': True, 'password': self.password_from_field}
            self.update_accounts_in_db(new_account)
            self.login()

    def update_accounts_in_db(self, new_account=None):
        password = new_account['password']
        password_encode = base64.b85encode(password.encode("utf-8"))
        logging.info(f"save account in db {new_account}")

        accounts = self.session.query(ModelAccount)
        try:
            if accounts[0]:
                for a in accounts:
                    a.current = 0
                    self.session.merge(a)
        except Exception as e:
            logging.error(f"update_accounts_in_db: {e} ")

        new_account['password'] = password_encode
        self.account = ModelAccount(**new_account)
        self.session.merge(self.account)
        self.account.password = password
        self.session.commit()
        self.session.close()

    @staticmethod
    def failure(request, results):
        print("failure")
        Snackbar(text=results['errors'][0]['message'], padding="20dp").open()

    def on_focus(self, instance, value):
        if value:
            pass
        else:
            if instance == self.name: self.check_name()
            if instance == self.user and self.user.text != '': self.check_account()
            if instance == self.password and self.password.text != '': self.check_pass1()
            if instance == self.second_password: self.check_pass2()
            if instance == self.email and self.email.text != '': self.check_email()

    def check_name(self):
        if self.name.text == '':
            Snackbar(text="Tú nombre es necesario.", padding="20dp").open()
            return False
        return True

    def check_account(self):
        user = "." + self.user.text.lower()
        if user == '':
            Snackbar(text="Nombre de cuenta es requerido", padding="20dp").open()
            return False

        if len(user) < 5 or len(user) > 15:
            Snackbar(text="Nombre de cuenta entre 5 y 15 caracteres ", padding="20dp").open()
            return False

        return True

    def check_pass1(self):
        password = self.password.text
        if (password != '' and len(password) >= 6) and len(password) <= 15:
            pass1_check = True
        else:
            Snackbar(text="La contraseña tiene que tener como mínimo 6 caracteres", padding="20dp").open()
            pass1_check = False
        return pass1_check

    def check_pass2(self):
        passwordSecond = self.second_password.text

        if passwordSecond != self.password.text:
            Snackbar(text="Las contraseñas no coinciden", padding="20dp").open()
            pass2_check = False
            return pass2_check

        if ((passwordSecond != '' and len(passwordSecond) >= 6) and len(
                passwordSecond) <= 15) and passwordSecond == self.password.text:
            pass2_check = True
        else:
            pass2_check = False
        self.second_password.hint_text = "Repetir contraseña"
        return pass2_check

    def check_email(self):
        email = self.email.text.lower()
        if email.find(" ") > -1:
            Snackbar(text="Email no puede contener espacios en blanco.", padding="20dp").open()
            email_check = False
            return email_check

        if email.find("@") == -1 or email.find(".") == -1:
            Snackbar(text="Email no valido.", padding="20dp").open()
            email_check = False
            return email_check

        if email == '':
            Snackbar(text="Email es requerido", padding="20dp").open()
            email_check = False
            return email_check
        return True

    def to_create_account(self):
        user = "." + self.user.text
        password = self.password.text
        email = self.email.text
        name = self.name.text
        A = self.check_account()
        B = self.check_pass1()
        C = self.check_pass2()
        D = self.check_email()
        E = self.check_name()

        if E is True and A is True and B is True and C is True and D is True:
            self.password_from_field = password
            self.create_task_account(name, user, self.password_from_field, email)
        else:
            if A is False:
                Snackbar(text="Nombre de cuenta no valido", padding="20dp").open()
            if B is False or D is False:
                Snackbar(text="Contraseña no valida", padding="20dp").open()
            if C is False:
                Snackbar(text="Email invalido", padding="20dp").open()
            if E is False:
                Snackbar(text="El campo nombre es requerido", padding="20dp").open()

    def login(self):
        logging.info("GO IN !")
        self.mainwid.class_login.go_in(self.account)

    def back_to_login(self):
        self.mainwid.login_screen()