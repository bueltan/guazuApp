from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.snackbar import Snackbar
from login_class.login_database import load_account_from_db, save_account
from login_class.login_payload import check_login, get_data_account
import hashlib

class Login(MDBoxLayout):

    def __init__(self, mainwid, **kwargs):
        super(Login, self).__init__()
        self.mainwid = mainwid
        self.keepOpen.on_release = lambda: self.change_ck()
        self.data_login = {'my_id': '', 'my_user_name': ''}
        account = load_account_from_db()
        try:
            self.ck_keepOpen.active = account.keepOpen
        except:
            pass
        if self.ck_keepOpen.active:
            if account:
                self.user.text = account.idName.split(".")[1]
                self.password.text = account.password

    def change_ck(self):
        if not self.ck_keepOpen.active:
            self.ck_keepOpen.active = True
        else:
            self.ck_keepOpen.active = False

    def go_in(self):
        # DELETE THIS DON'T FORGET
        connection = True
        user = "." + self.user.text
        user = user.lower()
        password = self.password.text
        id = check_login(user, password)
        print("ID USER:", id)
        if id:
            self.mainwid.goto_mainNavigation(account_name=user, account_id=id)
            print("global nested")
            self.data_login['my_id'] = id
            keepOpen = self.ck_keepOpen.active
            if connection:
                data = get_data_account(id)
                data['id'] = id
                data['keepOpen'] = keepOpen
                save_account(data)
        if id is None:
            Snackbar(text="Incorrect user name or password", padding="20dp").open()
        if id is False:
            Snackbar(text="lost connection", padding="20dp").open()

    def go_to_register(self):
        self.mainwid.goto_register()
