import os
from kivy.loader import Loader
from kivymd import images_path
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen
from login_class.login import Login
from register_class.register import Register
from main_navigation.main_navigation import MainNavigation
from kivy.core.window import Window
import asyncio
from assets.eval_func_speed import runtime_log
from sync_data.sync_data import SyncData
from sync_data.sync_subscriptions import SyncSubscriptions
import kivy.app
import plyer


class MainWid(ScreenManager):
    def __init__(self, **kwargs):
        super(MainWid, self).__init__()
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

        self.goto_login()

    def goto_login(self):
        self.current = 'loginScreen'
        self.Login.load_account_from_db()

    def goto_register(self):
        self.current = 'RegisterScreen'

    async def goto_mainNavigation(self, **kwargs):
        await SyncData(**kwargs).sync_subscriptions(3)
        self.current = 'mainNavigationScreen'
        account = kwargs.get('account')
        self.mainNavigation.load_subscriptions_from_db(account)


class MainApp(MDApp):
    def app_func(self):
        async def run_wrapper():
            await self.async_run(async_lib='asyncio')
            print('App done')

        return asyncio.gather(run_wrapper())

    async def check_connection(self):
        try:
            await asyncio.sleep(2)
        except asyncio.CancelledError as e:
            print('Wasting time was canceled', e)
        finally:
            # when canceled, print that it finished
            print('Done wasting time')

    def build(self):
        Loader.loading_image = f"{images_path}transparent.png"
        self.load_kv("register_class/register.kv")
        self.load_kv("login_class/login.kv")
        self.load_kv("main_navigation/card_subscription.kv")
        self.load_kv("main_navigation/main_navigation.kv")

        self.title = 'GuazuApp'
        Window.size = (400, 800)  # more common dimensions for mobiles, delete this for building
        self.theme_cls.primary_palette = "Purple"  # "Purple", "Red"
        self.theme_cls.theme_style = "Light"  # ""
        self.theme_cls.primary_hue = "900"  # "500"

        return MainWid()

    def on_start(self):
        #self.fps_monitor_start()
        plyer.notification.notify(title='test', message="Notification using plyer")
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