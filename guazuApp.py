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
from kivy.core.window import Window
from sync_data.sync_data import SyncData
from sync_data.Update_Interface import UpdateInterface
from sync_data.tunnel_subscriptions import TunnelSubscriptions
from assets.eval_func_speed import runtime_log


class GuazuApp(ScreenManager):
    def __init__(self, **kwargs):
        super(GuazuApp, self).__init__()
        self.Login = Login(self)
        self.Register = Register(self)
        wid = Screen(name='loginScreen')
        wid.add_widget(self.Login)
        self.add_widget(wid)
        self.mainNavigation = MainNavigation()
        wid = Screen(name='mainNavigationScreen')
        wid.add_widget(self.mainNavigation)
        self.add_widget(wid)
        wid = Screen(name='RegisterScreen')
        wid.add_widget(self.Register)
        self.add_widget(wid)
        self.Update_interface = UpdateInterface(self)
        self.TunnelSubscriptions = TunnelSubscriptions(self)
        self.SyncData = SyncData(self)
        self.goto_login()

    def goto_login(self):
        self.current = 'loginScreen'
        self.Login.load_account_from_db()

    def goto_register(self):
        self.current = 'RegisterScreen'

    async def open_tunnel(self, subscription_id= None, timestamp=0):
        if self.account:
            subscriptions = ModelSubscriptions.query.filter_by(id_account=functions.decode(self.account.id))
            if subscription_id is None:
                for subscription in subscriptions:
                    await self.TunnelSubscriptions.tunnel_subscriptions(subscription_id=subscription.id,
                                                                        timestamp=subscription.last_sync_timestamp)
            else:
                await self.TunnelSubscriptions.tunnel_subscriptions(subscription_id=subscription_id,
                                                                    timestamp=timestamp)

    async def goto_mainNavigation(self, **kwargs):
        self.account = kwargs.get('account')
        self.current = 'mainNavigationScreen'
        await self.SyncData.sync_subscriptions(self.account, 3)
        self.mainNavigation.load_subscriptions_from_db(self.account)
        logging.info("Is time to open tunnel")
        logging.info("asyncio %s", asyncio.as_completed)
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

        self.title = 'GuazuApp'
        Window.size = (540, 960)  # more common dimensions for mobiles, delete this for building
        self.theme_cls.primary_palette = "Teal"  # "Purple", "Red"
        self.theme_cls.theme_style = "Light"  # ""
        self.theme_cls.primary_hue = "900"  # "500"

        return GuazuApp()

    def on_start(self):
        self.fps_monitor_start()
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