from kivy.app import App
from kivy.base import Builder
from kivy.uix.label import Label


Builder.load_file('CHLabel.kv')


class CHLabel(Label):
    """中文输入框"""
    pass
