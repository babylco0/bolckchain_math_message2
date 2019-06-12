from kivy.app import App
from kivy.base import Builder
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton


Builder.load_file('CHButton.kv')


class CHButton(Button):
    """中文字体按钮"""
    pass


class CHToggleButton(ToggleButton):
    """中文字体按钮"""
    pass
