import logging
import asyncio
from kivy.core.text import LabelBase
from kivy.loader import Loader
from kivymd import images_path
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen
from database.model_subscription import ModelSubscriptions
from general_functions import functions
from login_class.login import Login
from path import assets_fonts
from register_class.register import Register
from main_navigation.main_navigation import MainNavigation
from main_navigation.conversations_messages import MessagesScreen
from kivy.core.window import Window
from sync.sync_data import SyncData
from sync.update_Interface import UpdateInterface
from sync.tunnel_subscriptions import TunnelSubscriptions
from assets.eval_func_speed import runtime_log


class GuazuApp(ScreenManager):
    def __init__(self, **kwargs):
        super(GuazuApp, self).__init__()
        self.account = None
        self.class_login = Login(self)
        self.class_register = Register(self)
        self.class_screen_messages = MessagesScreen(self)
        wid = Screen(name='MessagesScreen')
        wid.add_widget(self.class_screen_messages)
        self.add_widget(wid)

        wid = Screen(name='loginScreen')
        wid.add_widget(self.class_login)
        self.add_widget(wid)

        self.class_main_navigation = MainNavigation(self)
        wid = Screen(name='mainNavigationScreen')
        wid.add_widget(self.class_main_navigation)
        self.add_widget(wid)
        wid = Screen(name='RegisterScreen')
        wid.add_widget(self.class_register)
        self.add_widget(wid)
        self.class_update_interface = UpdateInterface(self)
        self.class_tunnel_subscriptions = TunnelSubscriptions(self)
        self.class_sync_data = SyncData(self)
        self.goto_login()

    def goto_messages(self, **kwargs):
        self.transition.direction = 'left'
        self.current = 'MessagesScreen'
        self.class_screen_messages.set_ticket(**kwargs)

    def goto_login(self):
        self.account = self.class_login.load_account_from_db()
        if not self.account:
            self.current = 'loginScreen'
        else:
            if not self.account.keepOpen:
                self.current = 'loginScreen'

    def goto_register(self):
        self.current = 'RegisterScreen'

    async def open_tunnel(self, subscription_id=None, timestamp=0):
        if self.account:
            subscriptions = ModelSubscriptions.query.filter_by(id_account=functions.decode(self.account.id))
            if subscription_id is None:
                for subscription in subscriptions:
                    await self.class_tunnel_subscriptions.\
                        tunnel_subscriptions(subscription_id=subscription.id,
                                             timestamp=subscription.last_sync_timestamp)
            else:
                await self.class_tunnel_subscriptions.tunnel_subscriptions(subscription_id=subscription_id,
                                                                           timestamp=timestamp)

    async def goto_main_navigation(self, **kwargs):
        logging.debug("goto_main_navigation")
        self.account = kwargs.get('account')
        self.current = 'mainNavigationScreen'
        self.class_main_navigation.load_subscriptions_from_db(self.account)
        await self.class_sync_data.sync_subscriptions(self.account, 3)
        logging.info("Is time to open tunnel")
        logging.info("asyncio %s", asyncio.as_completed)
        await self.open_tunnel()

    async def check_connection(self):
        logging.info("check_connection")
        result = await self.class_login.validate_account()
        logging.warning(f"result validation {result} ")
        await self.class_sync_data.sync_subscriptions(self.account, 3)
        await self.open_tunnel()


class MainApp(MDApp):
    LabelBase.register(name='UbuntuEmoji',
                       fn_regular=assets_fonts + 'Ubuntu-Regular.pfb')

    def app_func(self):
        async def run_wrapper():
            await self.async_run(async_lib='asyncio')
            print('App done')

        return asyncio.gather(run_wrapper())




    @runtime_log
    def build(self):
        Loader.loading_image = f"{images_path}transparent.png"
        self.load_kv("register_class/register.kv")
        self.load_kv("login_class/login.kv")
        self.load_kv("main_navigation/card_subscription.kv")
        self.load_kv("main_navigation/main_navigation.kv")
        self.load_kv("main_navigation/conversations_messages.kv")
        self.title = 'GuazuApp'
        Window.size = (540, 960)  # more common dimensions for mobiles, delete this for building
        self.theme_cls.primary_palette = "Teal"  # "Purple", "Red"
        self.theme_cls.theme_style = "Dark"  # ""
        self.theme_cls.accent_palette = "Blue"
        self.theme_cls.primary_hue = "900"  # "500"

        return GuazuApp()

    def on_start(self):
        # self.fps_monitor_start()
        return True

    def on_stop(self):
        return True

    def on_pause(self):
        return True

    def on_resume(self):
        return True


if __name__ == "__main__":

    loop = asyncio.get_event_loop()
    loop.run_until_complete(MainApp().app_func())
    loop.close()