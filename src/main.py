from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from TestScreen import *
from SelectUserScreen import *
from UserScreen import *


default_path = './demo_users.json'  # 默认用户密钥存储文件
message_path = './messages.json'  # 默认本地信息存储文件

sm = ScreenManager()  # screen manager
test_screen = TestScreen(name='test')
sel_user_screen = SelectUserScreen(name='sel_user')
user_screen = UserScreen(name='user')
sm.add_widget(test_screen)
sm.add_widget(sel_user_screen)
sm.add_widget(user_screen)
sm.current = 'sel_user'


def select_demo_user(sender):
    """选择测试用户"""
    # print(sender.text)
    # 加载测试用户信息成功显示用户界面
    if user_screen.init_user(sender.text, default_path, message_path):
        sm.direction = 'left'
        sm.current = 'user'
    else:
        sender.text = '用户失效'


#  绑定测试用户按钮事件
demo_users = sel_user_screen.ids['view_sel_user'].demo_users
for user in demo_users:
    demo_users[user].bind(on_press=select_demo_user)


class MainApp(App):
    def build(self):
        return sm


if __name__ == '__main__':
    MainApp().run()
