from kivy.app import App
from kivy.base import Builder
from kivy.uix.textinput import TextInput


Builder.load_file('CHTextInput.kv')


class CHTextInput(TextInput):
    """中文输入框"""
    pass
