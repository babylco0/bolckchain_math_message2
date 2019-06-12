import json

from kivy.base import Builder
from kivy.storage.jsonstore import JsonStore
from kivy.uix.boxlayout import BoxLayout
from MMUser import *
from MessageWidget import *
from CHLabel import *
from MMMessage import *


Builder.load_file('PublicWidget.kv')


class PublicWidget(BoxLayout):
    """公开信息界面"""
    message_path = ""  # 信息存储位置
    user = ""  # 用户
    contacts = {}  # 联系人地址-姓名对照表

    def __init__(self, user, m_path, contacts, **kwargs):
        """初始化"""
        super(PublicWidget, self).__init__(*kwargs)
        self.user = user
        self.message_path = m_path
        self.contacts = contacts
        self.load_history()

    def load_history(self):
        """加载聊天历史"""
        try:
            # 读取本地信息列表
            store = JsonStore(self.message_path)
            b_height = store.get('block')['height']
            while b_height > 0:
                msg_hash = store[str(b_height - 1)]['hash']
                msg_data = json.loads(store[msg_hash]['message'])
                message = MMMessage(msg_data)
                # 接收地址为公开,即‘0’
                if message.receiver == PUBLIC_ADDRESS:
                    s_address = message.sender
                    if message.sender in self.contacts:
                        s_name = self.contacts[message.sender]['name']
                    elif message.sender == self.user.address:
                        s_name = self.user.user_name
                    else:
                        s_name = None
                    s_content = self.user.decode_message(message)
                    msg_widget = MessageWidget(s_name, s_address, s_content)
                    msg_widget.update()
                    self.ids['history_list'].add_widget(msg_widget)
                b_height -= 1
        except Exception as e:
            print(str(e))

    def send_message(self):
        """发送消息
        生成一侧公开信息，并存储在本地
        """
        content = self.ids['ti_message'].text
        if content is None:
            return
        message = self.user.create_public_message(content)
        if message is not None:
            print(message.serialize())
            # 将信息写入本地
            try:
                # 读取本地信息列表
                store = JsonStore(self.message_path)
                block_height = store.get('block')['height']
                if not store.exists(message.hash()):  # store message if not exist
                    store[block_height] = {'hash': message.hash()}
                    block_height += 1
                    store['block'] = {'height': block_height}
                    store[message.hash()] = {'message': message.serialize()}
            except Exception as e:
                print(str(e))
