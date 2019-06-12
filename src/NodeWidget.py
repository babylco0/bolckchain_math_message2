import json

from kivy.base import Builder
from kivy.network.urlrequest import UrlRequest
from kivy.uix.boxlayout import BoxLayout
from MessageWidget import *
from MMMessage import *
from kivy.uix.gridlayout import GridLayout

Builder.load_file('NodeWidget.kv')

message_hash = set()  # 本地信息哈希集合


class NodeWidget(BoxLayout):
    """节点配置界面"""

    def __init__(self, **kwargs):
        super(NodeWidget, self).__init__(**kwargs)
        self.server_layout = ServerLayout()
        self.sync_layout = SyncMessageLayout()
        self.add_widget(self.server_layout)
        self.ids['sync_test'].bind(on_press=self.sync_test)
        self.ids['conn_test'].bind(on_press=self.conn_test)

    def sync_test(self, sender):
        """加载信息同步界面"""
        if sender.state == 'down':
            self.remove_widget(self.server_layout)
            url = self.server_layout.ids['server_url'].text
            self.sync_layout.update_url(url)
            self.add_widget(self.sync_layout)

    def conn_test(self, sender):
        """加载信息同步界面"""
        if sender.state == 'down':
            self.remove_widget(self.sync_layout)
            self.add_widget(self.server_layout)

    def get_server_url(self):
        """获取服务器地址"""
        return self.server_layout.ids['server_url'].text


class ServerLayout(BoxLayout):
    """服务器测试布局"""

    def __init__(self, **kwargs):
        super(ServerLayout, self).__init__(**kwargs)

    def test_configure(self):
        """测试服务器连接状态"""
        url = self.ids['server_url'].text + 'test.php'
        req = UrlRequest(url=url,
                         on_success=self.request_success,
                         on_failure=self.request_failure,
                         on_error=self.request_failure)

    def request_success(self, req, values):
        """请求成功"""
        if values == 'OK':
            self.ids['test_statues'].text = '连接服务器<[color=33ff33]成功[/color]>'

    def request_failure(self, req, result):
        """请求失败"""
        self.ids['test_statues'].text = '连接服务器<[color=ff3333]失败[/color]>'


class SyncMessageLayout(BoxLayout):
    """服务器测试布局"""

    def __init__(self, **kwargs):
        super(SyncMessageLayout, self).__init__(**kwargs)
        self.sync_count_success = 0
        self.sync_count_failure = 0
        self.layout = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.layout.bind(minimum_height=self.layout.setter('height'))

    def update_url(self, url):
        """更新服务器地址"""
        self.ids['server_url'].text = url

    def sync_messages(self):
        """同步服务器信息"""
        url = self.ids['server_url'].text + 'height.php'  # 获取信息高度（条目数）
        self.sync_count_success = 0
        self.sync_count_failure = 0
        self.ids['scrlv'].clear_widgets()
        self.layout.clear_widgets()
        req = UrlRequest(url=url, on_success=self.get_height_success)

    def get_height_success(self, req, values):
        """获取信息高度成功后逐条目同步信息"""
        all_hash = json.loads(values)
        # self.ids['message_list'].text = "获取信息高度成功< " + str(len(all_hash)) + "> \n"
        for h in all_hash:
            if h not in message_hash:
                url = self.ids['server_url'].text + 'get_hash.php' + '?hash=' + h
                req = UrlRequest(url=url, on_success=self.request_success)

    def request_success(self, req, values):
        """请求成功"""
        self.sync_count_success += 1
        dat = json.loads(str(values))
        message = MMMessage(json.loads(dat))
        msg = MessageLayout(message)
        msg.update()
        self.ids['scrlv'].clear_widgets()
        self.layout.add_widget(msg)
        self.ids['scrlv'].add_widget(self.layout)
        # self.ids['message_list'].text += '信息<' + str(self.sync_count_success) + ">\n" + json.loads(values) + "\n"
        self.ids['sync_statues'].text = '成功同步[color=33ff33]{0}[/color]失败[color=ff3333]{1}[/color]'.format(
            str(self.sync_count_success),
            str(self.sync_count_failure))

    def request_failure(self, req, result):
        """请求失败"""
        # self.ids['message_list'].text += "请求失败\n"
        self.sync_count_failure += 1
        self.ids['sync_statues'].text = '成功同步[color=33ff33]{0}[/color]失败[color=ff3333]{1}[/color]'.format(
            str(self.sync_count_success),
            str(self.sync_count_failure))
