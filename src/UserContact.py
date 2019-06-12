from kivy.app import App
from kivy.base import Builder
from kivy.uix.boxlayout import BoxLayout
from CHButton import *


Builder.load_file('UserContact.kv')


class ContactLayout(BoxLayout):
    """联系人卡片布局"""
    default_size = 24
    name = ""
    address = ""
    pubkey = ""

    def __init__(self, u_name=None, u_address=None, u_pubkey=None, **kwargs):
        super(ContactLayout, self).__init__(**kwargs)
        self.name = u_name
        self.address = u_address
        self.pubkey = u_pubkey

    def update(self):
        """更新联系人卡片显示"""
        self.ids['u_name'].text = self.name
        self.ids['u_address'].text = self.address
        self.ids['u_pubkey'].text = self.pubkey
