from kivy.base import Builder
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from CHButton import *
from Configure import *


Builder.load_file('SelectUserScreen.kv')


class SelectUserScreen(Screen):
    pass


class SelectUserView(ScrollView):
    """选择用户视图"""
    demo_users = {}

    def __init__(self, **kwargs):
        """构造函数"""
        super(SelectUserView, self).__init__(**kwargs)
        layout = GridLayout(cols=1, spacing=10, size_hint_y=None, height=1024)
        layout.bind(minimum_height=layout.setter('height'))
        # 添加已有测试用户按钮
        for name in demo_user_names:
            c = CHButton(text=name, size_hint_y=None, height=160)
            self.demo_users[name] = c
            layout.add_widget(c)
        # 添加新建用户按钮
        c = CHButton(text="新建用户", size_hint_y=None, height=160)
        # self.demo_users[name] = c
        layout.add_widget(c)
        self.size_hint = (1, 1)
        self.add_widget(layout)

