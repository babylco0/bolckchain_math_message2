import json
from urllib import parse

from kivy.base import Builder
from kivy.network.urlrequest import UrlRequest
from kivy.storage.jsonstore import JsonStore
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from CHButton import *
from CHTextInput import *
from CHLabel import *
from Configure import *
from UserContact import *
from MineWidget import *
from NodeWidget import *
from MessageWidget import *
from ChatWidget import *
from util import *
from MMUser import *
from MMMessage import *
from PublicWidget import *
from secp256k1 import PrivateKey, PublicKey
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA
from Crypto.Cipher import PKCS1_v1_5
from Crypto import Random
import binascii

Builder.load_file('UserScreen.kv')
help_text = """
**帮助信息**
===========
点击<[color=ff3333]私有信息[/color]>按钮 -> 查看对话信息
点击<[color=ff3333]公开信息[/color]>按钮 -> 查看公开信息
点击<[color=ff3333]联系人[/color]>按钮 -> 查看联系人列表
点击<[color=ff3333]个人信息[/color]>按钮 -> 查看个人地址密钥等信息
点击<[color=ff3333]重新选择[/color]>按钮 -> 重新选择测试用户
点击<[color=ff3333]配置信息[/color]>按钮 -> 查看节点配置信息
点击<[color=ff3333]用户名[/color]>按钮 -> 同步服务器与本地信息
点击<[color=ff3333]扫一扫[/color]>按钮 -> 添加好友或节点等
"""


class ContactView(ScrollView):
    """联系人视图"""
    user_name = ""  # 用户名
    contact_path = ""  # 默认联系人存储位置
    contacts = {}  # 联系人地址-姓名对照表

    def __init__(self, **kwargs):
        """构造函数"""
        super(ContactView, self).__init__(**kwargs)

    def load_contacts(self, u_name, c_path):
        """显示除自己外的所有测试用户信息"""
        self.user_name = u_name
        self.contact_path = c_path
        self.contacts.clear()
        layout = GridLayout(cols=1, spacing=10, size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))
        self.clear_widgets()
        try:
            store = JsonStore(self.contact_path)
            for name in demo_user_names:
                if name == self.user_name:
                    continue
                address = store.get(name)['address']
                pubkey = store.get(name)['rsa_pubkey']
                c = ContactLayout(u_name=name,
                                  u_address=address,
                                  u_pubkey=pubkey)
                self.contacts[address] = {'name': name, 'pubkey': pubkey, 'control': c}  # (name, pubkey, c)
                c.update()
                layout.add_widget(c)
        except Exception as e:
            print(str(e))
        self.size_hint = (1, 1)
        self.add_widget(layout)


class AllMessage(object):
    """本地所有信息"""

    def __init__(self):
        self.message_path = ""
        self.message_hash = set()
        self.block_height = 0

    def load_local_messages(self, m_path):
        """加载本地信息"""
        self.message_path = m_path
        self.message_hash.clear()
        self.block_height = 0
        try:
            message_store = JsonStore(self.message_path)
            if not message_store.exists('block'):  # initialize block info
                message_store.put('block', height=0)
            else:
                self.block_height = message_store.get('block')['height']
                for i in range(0, self.block_height):
                    msg_hash = message_store[str(i)]['hash']
                    self.message_hash.add(msg_hash)
                    # print(i, msg_hash)
        except Exception as e:
            print(str(e))

    def save_messages(self, msg):
        """存储信息至本地"""
        try:
            store = JsonStore(self.message_path)
            if not store.exists(msg.hash()):  # store message if not exist
                store[self.block_height] = {'hash': msg.hash()}
                self.block_height += 1
                store['block'] = {'height': self.block_height}
                store[msg.hash()] = {'message': msg.serialize()}
            self.message_hash.add(msg.hash())
        except Exception as e:
            print(str(e))


class ChatMessageView(ScrollView):
    """对话信息列表视图"""
    user = ""  # 用户
    message_path = ""  # 默认联系人存储位置
    contacts = {}  # 联系人地址-姓名对照表

    def __init__(self, user=None, m_path=None, u_contact=None, **kwargs):
        """构造函数"""
        super(ChatMessageView, self).__init__(**kwargs)
        self.user = user
        self.message_path = m_path
        self.contacts = u_contact

    def load_chat_messsages(self, user, u_contact, m_path):
        """显示除自己外的所有测试用户信息"""
        self.user = user
        self.message_path = m_path
        self.contacts = u_contact
        layout = GridLayout(cols=1, spacing=10, size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))
        self.clear_widgets()
        try:
            # 读取本地信息列表
            store = JsonStore(self.message_path)
            b_height = store.get('block')['height']
            while b_height > 0:
                msg_hash = store[str(b_height - 1)]['hash']
                msg_data = json.loads(store[msg_hash]['message'])
                message = MMMessage(msg_data)
                # 验证接收地址是自己的信息
                if self.user.is_mine(message) and verify_message(message):
                    if message.sender in self.contacts:
                        s_name = self.contacts[message.sender]['name']
                    elif message.sender == self.user.address:
                        s_name = self.user.user_name
                    else:
                        s_name = None
                    s_address = message.sender
                    s_content = self.user.decode_message(message)
                    msg_widget = MessageWidget(s_name, s_address, s_content)
                    msg_widget.update()
                    layout.add_widget(msg_widget)
                b_height -= 1
            self.size_hint = (1, 1)
            self.add_widget(layout)
        except Exception as e:
            print('Error: ', str(e))


class UserScreen(Screen):
    """用户界面"""
    user_name = ""
    user_path = ""
    message_path = ""
    current_widget = None
    contact_widget = ContactView()
    mine_widget = MineWidget()
    node_widget = NodeWidget()
    local_messages = AllMessage()

    def __init__(self, **kwargs):
        """初始化"""
        super(UserScreen, self).__init__(**kwargs)
        # 用户信息
        self.user = MMUser()
        self.address = ""
        #  初始化帮助信息
        self.ids['doc_help'].text = help_text
        self.current_widget = self.ids['doc_help']
        #
        self.contact_widget = ContactView()
        self.mine_widget = MineWidget()
        self.node_widget = NodeWidget()
        # self.chat_list_widget = ChatMessageView()
        self.local_messages = AllMessage()
        self.get_count = 0
        self.post_count = 0

    def init_user(self, user, u_path, m_path):
        """设置用户名字"""
        ret = self.user.load_keys(user, u_path)
        if not ret:
            return False
        self.user_name = user
        self.user_path = u_path
        self.message_path = m_path
        self.address = self.user.address
        self.ids['user_name'].text = user
        # 个人卡片
        self.mine_widget.set_user(self.user)
        # 联系人卡片
        self.contact_widget.load_contacts(self.user_name, self.user_path)  # 加载联系人列表
        for c in self.contact_widget.contacts:  # 绑定联系人点击事件
            # print(self.contact_widget.contacts[c]['control'].ids['u_name'].text)
            self.contact_widget.contacts[c]['control'].ids['u_address'].bind(on_press=self.c_address_clicked)
            self.contact_widget.contacts[c]['control'].ids['u_name'].bind(on_press=self.c_name_clicked)
            self.contact_widget.contacts[c]['control'].ids['u_pubkey'].bind(on_press=self.c_pubkey_clicked)
        # 对话列表
        # self.chat_list_widget.load_chat_messsages(self.user, self.contact_widget.contacts, self.message_path)
        # 本地信息
        self.local_messages.load_local_messages(self.message_path)
        # print(self.local_messages.message_hash)
        self.show_help()
        return True

    def right_top_clicked(self):
        """右上按钮事件"""
        self.show_configure()

    def show_help(self):
        """显示帮助界面"""
        self.ids['label_tips'].text = "<点击对应按钮开始测试>"
        self.ids['main_widget'].remove_widget(self.current_widget)
        self.current_widget = self.ids['doc_help']
        self.ids['main_widget'].add_widget(self.current_widget)
        self.ids['user_name'].text = self.user_name

    def show_mine(self):
        """显示个人信息"""
        self.ids['label_tips'].text = "<点击对应按钮显示个人密钥值>"
        self.ids['main_widget'].remove_widget(self.current_widget)
        self.current_widget = self.mine_widget
        self.ids['main_widget'].add_widget(self.current_widget)

    def show_private(self):
        """显示个人对话信息"""
        self.ids['label_tips'].text = "<显示与我相关的对话信息>"
        chat_list_widget = ChatMessageView(self.user, self.contact_widget.contacts, self.message_path)
        chat_list_widget.load_chat_messsages(self.user, self.contact_widget.contacts, self.message_path)
        self.ids['main_widget'].remove_widget(self.current_widget)
        self.current_widget = chat_list_widget
        self.ids['main_widget'].add_widget(self.current_widget)

    def send_message(self, sender):
        """发送信息至服务器"""
        self.sync_messages()

    def sync_messages(self):
        """同步服务器信息"""
        self.ids['label_tips'].text = "<信息同步中>"
        url = self.node_widget.get_server_url() + 'height.php'  # 获取信息高度（条目数）
        self.get_count = 0
        self.post_count = 0
        req = UrlRequest(url=url, on_success=self.get_height_success)

    def get_height_success(self, req, values):
        """获取信息高度成功后逐条目同步信息"""
        all_hash = json.loads(values)
        self.local_messages.load_local_messages(self.message_path)
        for h in all_hash:
            # 同步服务器端信息
            if h not in self.local_messages.message_hash:
                url = self.node_widget.get_server_url() + 'get_hash.php' + '?hash=' + h
                req = UrlRequest(url=url, on_success=self.request_success)
        # 发送本地信息至服务器
        for h in self.local_messages.message_hash:
            if h not in all_hash:
                # 读取本地信息内容
                try:
                    store = JsonStore(self.message_path)
                    data = json.loads(store[h]['message'])
                    data['hash'] = h
                    params = parse.urlencode(data)
                    url = self.node_widget.get_server_url() + 'post.php' + '?' + params
                    req = UrlRequest(url=url, on_success=self.send_success,
                                     on_failure=self.request_failure,
                                     on_error=self.request_failure)
                except Exception as e:
                    print(str(e))
        self.ids['label_tips'].text = "<信息同步完成>"

    def send_success(self, req, values):
        """发送信息成功"""
        self.post_count += 1
        self.ids['label_tips'].text = "成功接受<{0}>条信息发送<{1}>条信息".format(self.get_count, self.post_count)

    def request_success(self, req, values):
        """请求成功"""
        dat = (json.loads(values))
        msg = MMMessage(data=json.loads(dat))
        if msg is not None:
            self.get_count += 1
            self.local_messages.save_messages(msg)
            self.ids['label_tips'].text = "成功接受<{0}>条信息发送<{1}>条信息".format(self.get_count, self.post_count)

    def request_failure(self, req, result):
        """请求失败"""
        pass

    def show_public(self):
        """显示公开信息"""
        self.ids['label_tips'].text = "<显示公开信息>"
        self.ids['main_widget'].remove_widget(self.current_widget)
        public_widget = PublicWidget(self.user, self.message_path, self.contact_widget.contacts)
        public_widget.ids['button_send'].bind(on_press=self.send_message)
        self.current_widget = public_widget
        self.ids['main_widget'].add_widget(self.current_widget)

    def show_configure(self):
        """显示配置界面"""
        self.ids['label_tips'].text = "<网络配置信息>"
        self.ids['main_widget'].remove_widget(self.current_widget)
        self.current_widget = self.node_widget
        self.ids['main_widget'].add_widget(self.current_widget)

    def middle_top_clicked(self):
        """显示主页"""
        self.sync_messages()

    def show_contact(self):
        """显示联系人信息"""
        self.ids['label_tips'].text = "<点击联系人开始对话>"
        self.ids['main_widget'].remove_widget(self.current_widget)
        self.current_widget = self.contact_widget
        self.ids['main_widget'].add_widget(self.current_widget)

    def c_address_clicked(self, sender):
        """地址按键事件"""
        self.show_chat_dlg(sender.text)

    def c_name_clicked(self, sender):
        """联系人头像按键事件"""
        c_name = sender.text
        for c in self.contact_widget.contacts:  # 绑定联系人点击事件
            if self.contact_widget.contacts[c]['name'] == c_name:
                self.show_chat_dlg(c)

    def c_pubkey_clicked(self, sender):
        """联系人头像按键事件"""
        c_pubkey = sender.text
        for c in self.contact_widget.contacts:  # 绑定联系人点击事件
            if self.contact_widget.contacts[c]['pubkey'] == c_pubkey:
                self.show_chat_dlg(c)

    def show_chat_dlg(self, c):
        """显示聊天框"""
        self.ids['label_tips'].text = "<与[color=ff3333] {0} [/color]聊天中>".format(self.contact_widget.contacts[c]['name'])
        t_contact = {'name': self.contact_widget.contacts[c]['name'],
                     'address': c,
                     'pubkey': self.contact_widget.contacts[c]['pubkey']}
        chat_widget = ChatWidget(self.user, t_contact, self.message_path)
        chat_widget.ids['button_send'].bind(on_press=self.send_message)
        self.ids['main_widget'].remove_widget(self.current_widget)
        self.current_widget = chat_widget
        self.ids['main_widget'].add_widget(self.current_widget)



