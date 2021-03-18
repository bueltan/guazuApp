import logging
import urllib

from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
import requests
from kivy.network.urlrequest import UrlRequest
from functools import partial
from kivymd.app import MDApp
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s — %(name)s — %(levelname)s — %(funcName)s:%(lineno)d — %(message)s")

class MainApp(MDApp):
    def build(self):
        grid = GridLayout(cols=1)
        button1 = Button(text="Normal request")
        button2 = Button(text= "kivy request", on_release= self.run_UrlRequests)
        black_button = Button(text="Click me!")
        grid.add_widget(button1)
        grid.add_widget(button2)
        grid.add_widget(black_button)
        return grid

    def run_UrlRequests(self, *args):
        nodes  = "node"
        query =  '{"query":"{area_list {edges {'+nodes+' {id name_area}}}}"}'
        print("run_UrlRequests")
        headers = {'content-type': 'application/json'}
        for i in range(10000):
            self.r = UrlRequest("http://entity.ar:5000/graphql",
                                on_success=self.success,
                                on_failure=self.failure,
                                on_error=self.error,
                                req_body=query,
                                req_headers=headers,
                                debug=True)

    @staticmethod
    def success(request, results):
        print("success")
        print(results)

    @staticmethod
    def failure( request, results):
        print("failure")
        print(results)


    @staticmethod
    def error(request, error):
            print("error")
            print(error)

MainApp().run()