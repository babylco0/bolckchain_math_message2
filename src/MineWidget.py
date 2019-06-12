from kivy.base import Builder
from kivy.uix.boxlayout import BoxLayout


Builder.load_file('MineWidget.kv')


class MineWidget(BoxLayout):
    """个人信息界面"""
    address = ""
    rsa_prikey = ""
    rsa_pubkey = ""
    ecc_prikey = ""
    ecc_pubkey = ""
    aes_key = ""
    aes_iv = ""

    def __init__(self, **kwargs):
        """初始化函数"""
        super(MineWidget, self).__init__(**kwargs)

    def set_user(self, user):
        """设置用户"""
        self.address = user.address
        self.rsa_prikey = user.rsa_prikey
        self.rsa_pubkey = user.rsa_pubkey
        self.ecc_prikey = user.ecc_prikey
        self.ecc_pubkey = user.ecc_pubkey
        self.aes_key = user.aes_key
        self.aes_iv = user.aes_iv
