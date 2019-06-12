import json

from kivy.base import Builder
from kivy.storage.jsonstore import JsonStore
from kivy.uix.boxlayout import BoxLayout
from MMUser import *
from MessageWidget import *
from CHLabel import *
from MMMessage import *


Builder.load_file('ChatWidget.kv')


class ChatWidget(BoxLayout):
    """个人信息界面"""
    message_path = ""  # 信息存储位置
    user = ""  # 用户
    contact = {'name': None, 'address': None, 'pubkey': None}  # 联系人信息

    def __init__(self, user, contact, m_path, **kwargs):
        """构造函数"""
        super(ChatWidget, self).__init__(**kwargs)
        self.message_path = m_path
        self.user = user
        self.contact = contact
        self.load_history()

    def load_history(self):
        """加载聊天历史"""
        self.ids['history_list'].clear_widgets()
        try:
            # 读取本地信息列表
            store = JsonStore(self.message_path)
            b_height = store.get('block')['height']
            while b_height > 0:
                msg_hash = store[str(b_height - 1)]['hash']
                msg_data = json.loads(store[msg_hash]['message'])
                message = MMMessage(msg_data)
                # 接受的信息
                if message.receiver == self.user.address and message.sender == self.contact['address']:
                    content = self.user.decode_message(message)
                    msg_text = "{0}:<{1}>@[{2}]".format(self.contact['name'], content, msg_data['time'])
                    msg = ChatMessageRecv(text=msg_text)
                    self.ids['history_list'].add_widget(msg)
                # 发送的信息
                if message.receiver == self.contact['address'] and message.sender == self.user.address:
                    content = self.user.decode_message(message)
                    msg_text = "{0}:<{1}>@[{2}]".format(self.user.user_name, content, msg_data['time'])
                    msg = ChatMessageSend(text=msg_text)
                    self.ids['history_list'].add_widget(msg)
                b_height -= 1
        except Exception as e:
            print(str(e))

    def send_message(self):
        """发送消息
        生成一侧对话信息，并存储在本地
        """
        content = self.ids['ti_message'].text
        if content is None:
            return
        message = self.user.create_chat_message(self.contact['address'], self.contact['pubkey'], content)
        if message is not None:
            # print(message.serialize())
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


