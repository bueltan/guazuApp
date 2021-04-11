import logging
import asyncio
from kivy.core.text import LabelBase
from kivymd.app import MDApp
from kivy.base import EventLoop
from kivy.core.audio import SoundLoader
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.font_definitions import theme_font_styles
from path import assets_fonts
from sync.sync_data import SyncData
from update_Interface import UpdateInterface
from login_class.login import Login
from register_class.register import Register
from main_navigation.main_navigation import MainNavigation
from main_navigation.conversations_messages import MessagesScreen


logger = logging.getLogger('my-logger')
logger.propagate = False


class GuazuApp(ScreenManager):
    def __init__(self, **kwargs):
        super(GuazuApp, self).__init__()
        EventLoop.window.bind(on_keyboard=self.hook_keyboard)
        self.account = None
        self.checking = False

        self.class_login = Login(self)
        wid = Screen(name='loginScreen')
        wid.add_widget(self.class_login)
        self.add_widget(wid)

        self.goto_login()
        self.class_register = None
        self.class_screen_messages = None

    def hook_keyboard(self, window, key, *largs):
        if key == 27:
            print("go back")
            if self.current == 'MessagesScreen':
                self.current = 'mainNavigationScreen'
            if self.current == 'RegisterScreen':
                self.current = 'loginScreen'
        return True

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

    def login_screen(self):
        self.transition.direction = 'left'
        self.current = 'loginScreen'

    def goto_register(self):
        if self.class_register is None:
            self.class_register = Register(self)
            wid = Screen(name='RegisterScreen')
            wid.add_widget(self.class_register)
            self.add_widget(wid)

        self.current = 'RegisterScreen'

    def playsound(self, effect=None):
        if effect == 'new_message_from_me':
            sound = SoundLoader.load('assets/done-for-you-cut.wav')
            sound.play()
        if effect == 'new_bubble':
            sound = SoundLoader.load('assets/bubble-pop-notification-V1-cut.wav')
            sound.play()

    async def goto_main_navigation(self, **kwargs):
        logging.debug("goto_main_navigation")
        self.class_update_interface = UpdateInterface(self)
        self.class_sync_data = SyncData(self)
        self.class_main_navigation = MainNavigation(self)

        wid = Screen(name='mainNavigationScreen')
        wid.add_widget(self.class_main_navigation)
        self.add_widget(wid)

        self.account = kwargs.get('account')
        self.current = 'mainNavigationScreen'
        self.class_main_navigation.load_subscriptions_from_db(self.account)

        await self.class_sync_data.sync_subscriptions(self.account, 3)

        if self.class_screen_messages is None:
            self.class_screen_messages = MessagesScreen(self)
            wid = Screen(name='MessagesScreen')
            wid.add_widget(self.class_screen_messages)
            self.add_widget(wid)

    async def check_connection(self):
        if not self.checking:
            logging.info("check_connection")
            self.checking = True
            await self.class_login.validate_account(reload=True)
        else:
            logging.warning("In this moment we are waiting for the validation")


class MainApp(MDApp):

    def app_func(self):
        async def run_wrapper():
            await self.async_run(async_lib='asyncio')
            print('App done')

        return asyncio.gather(run_wrapper())

    def build(self):
        LabelBase.register(name='UbuntuEmoji',
                           fn_regular=assets_fonts + 'Ubuntu-Regular.pfb')
        theme_font_styles.append('UbuntuEmojiStyle')

        self.theme_cls.font_styles["UbuntuEmojiStyle"] = [
            "UbuntuEmoji",
            14,
            False,
            0.15,
        ]
        self.load_kv("register_class/register.kv")
        self.load_kv("login_class/login.kv")
        self.load_kv("main_navigation/card_subscription.kv")
        self.load_kv("main_navigation/main_navigation.kv")
        self.load_kv("main_navigation/conversations_messages.kv")

        self.title = 'GuazuApp'
        self.theme_cls.primary_palette = "Purple"  # "Purple", "Red"
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
