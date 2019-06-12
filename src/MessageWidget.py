import json

from kivy.app import App
from kivy.base import Builder
from kivy.uix.boxlayout import BoxLayout
from CHButton import *
from util import *
from CHLabel import *
from MMMessage import *


Builder.load_file('MessageWidget.kv')


class MessageWidget(BoxLayout):
    """信息缩略图界面"""
    name = ""
    address = ""
    content = ""

    def __init__(self, s_name=None, s_address=None, s_content=None, **kwargs):
        super(MessageWidget, self).__init__(**kwargs)
        self.name = s_name
        self.address = s_address
        self.content = s_content

    def update(self):
        """更新信息内容"""
        if self.name is None:
            self.ids['s_name'].text = '?'
        else:
            self.ids['s_name'].text = self.name
        self.ids['s_address'].text = self.address
        self.ids['s_content'].text = self.content


class MessageLayout(BoxLayout):
    """信息对象"""
    default_size = 32

    def __init__(self, message=None, **kwargs):
        super(MessageLayout, self).__init__(**kwargs)
        self.message = message

    def update(self):
        """更新信息内容"""
        self.ids['btn_sender'].text = 'Sender: ' + self.message.sender
        self.ids['btn_receiver'].text = 'Receiver: ' + self.message.receiver
        self.ids['btn_content'].text = self.message.content
        self.ids['btn_time'].text = '@' + self.message.time


class ChatMessageSend(CHLabel):
    """发送的对话信息，右对齐"""
    pass


class ChatMessageRecv(CHLabel):
    """发送的对话信息，左对齐"""
    pass

