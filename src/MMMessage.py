import json
from util import *


class MMMessage(object):
    """信息对象"""
    '''
    sender = ""  # 发送者地址
    receiver = ""  # 接收者地址
    time = ""  # 发送时间
    content = ""  # 信息内容
    sign = ""  # 信息签名
    pubkey = ""  # 发信人公钥
    tkey  # 钥匙
    '''
    data = {'sender': None, 'receiver': None, 'time': None, 'content': None, 'sign': None, 'pubkey': None, 'ekey': None}

    def __init__(self, data=None):
        """构造函数"""
        if data is not None:
            for key in self.data:
                self.data[key] = data[key]

    def __setattr__(self, key, value):
        """设置值"""
        if key in self.data:
            self.data[key] = value

    def __getattr__(self, item):
        """获取值"""
        if item in self.data:
            return self.data[item]
        else:
            return None

    def serialize(self):
        """序列化信息内容"""
        return json.dumps(self.data)

    def hash(self):
        """返回信息哈希值"""
        return hash256(str(self.data).encode('utf-8'))

