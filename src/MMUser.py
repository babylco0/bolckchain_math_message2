from kivy.storage.jsonstore import JsonStore
from util import *
from MMMessage import *
from secp256k1 import PrivateKey, PublicKey
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA
from Crypto.Cipher import PKCS1_v1_5, AES
from Crypto import Random
import binascii
import time


class MMUser(object):
    """Math Message User Class
    用户类
    """
    user_name = ""  # 用户名
    user_path = ""  # 存储路径
    address = ""  # 地址
    __rsa_prikey = ""  # RSA 私钥
    rsa_pubkey = ""  # RSA 公钥
    __ecc_prikey = ""  # ECC 私钥
    ecc_pubkey = ""  # ECC 公钥
    __aes_key = ""  # AES 密钥
    __aes_iv = ""  # AES 初始向量

    def __init__(self, u_name=None, u_path=None):
        """初始化用户"""
        self.user_path = u_path
        self.user_name = u_name

    def load_keys(self, u_name=None, u_path=None):
        """加载用户密钥"""
        if u_name and u_path:
            self.user_path = u_path
            self.user_name = u_name
        try:
            store = JsonStore(self.user_path)
            self.address = store.get(self.user_name)['address']
            self.__rsa_prikey = store.get(self.user_name)['rsa_prikey']
            self.rsa_pubkey = store.get(self.user_name)['rsa_pubkey']
            self.__ecc_prikey = store.get(self.user_name)['ecc_prikey']
            self.ecc_pubkey = store.get(self.user_name)['ecc_pubkey']
            self.__aes_key = store.get(self.user_name)['aes_key']
            self.__aes_iv = store.get(self.user_name)['aes_iv']
            return True
        except Exception as e:
            return False, str(e)

    def __getattr__(self, item):
        if item == 'ecc_prikey':
            return self.__ecc_prikey
        if item == 'rsa_prikey':
            return self.__rsa_prikey
        if item == 'aes_iv':
            return self.__aes_iv
        if item == 'aes_key':
            return self.__aes_key

    def create_chat_message(self, r_address, r_pubkey, content):
        """生成对话信息
        Args:
            r_address: 接收者地址
            r_pubkey: 接收者公钥
            content: 信息明文
        Return:
            加密后的对话消息
        """
        chat_message = MMMessage()
        chat_message.sender = self.address
        chat_message.receiver = r_address
        chat_message.pubkey = self.ecc_pubkey
        if self.address == r_address:  # 发给自己的对话信息等同于私密信息
            chat_message.content = self.encrypt_content(MODE_KEY_IV, content)
        else:
            chat_message.content = self.encrypt_content(MODE_KEY_KEY, content)
        chat_message.ekey = self.encrypt_aes_key(r_pubkey)
        chat_message.sign = self.sign_content(chat_message.content)
        chat_message.time = str(time.asctime(time.localtime(time.time())))
        return chat_message

    def create_public_message(self, content):
        """生成公开信息
        Args:
            content: 信息明文
        Return:
            加密后的公开信息
        """
        public_message = MMMessage()
        public_message.sender = self.address
        public_message.receiver = PUBLIC_ADDRESS
        public_message.pubkey = self.ecc_pubkey
        public_message.content = self.encrypt_content(MODE_NONE, content)
        public_message.ekey = '0'
        public_message.sign = self.sign_content(public_message.content)
        public_message.time = str(time.asctime(time.localtime(time.time())))
        return public_message

    def create_private_message(self, content):
        """生成私密信息
        Args:
            content: 信息明文
        Return:
            加密后的私密信息
        """
        private_message = MMMessage()
        private_message.sender = self.address
        private_message.receiver = self.address
        private_message.pubkey = self.ecc_pubkey
        private_message.content = self.encrypt_content(MODE_KEY_IV, content)
        private_message.ekey = '0'
        private_message.sign = self.sign_content(private_message.content)
        private_message.time = str(time.asctime(time.localtime(time.time())))
        return private_message

    def sign_content(self, content):
        """签名消息"""
        ecc_prikey = PrivateKey(bytes(bytearray.fromhex(self.__ecc_prikey)))
        sign = ecc_prikey.ecdsa_sign(binascii.unhexlify(content))
        readable_sign = binascii.hexlify(ecc_prikey.ecdsa_serialize(sign)).decode('utf-8')
        return readable_sign

    def decode_message(self, message):
        """解码信息内容
        Args:
            message: 信息
        Return:
            content: 解码的信息明文
        """
        if message.receiver == PUBLIC_ADDRESS:  # 公开信息
            return self.decrypt_content(MODE_NONE, message.content)
        if message.sender != self.address and message.receiver != self.address:  # 接收者和发送者都不是自己，返回None
            return None
        if message.sender == self.address:
            if message.receiver == self.address:  # 发送者与接收者都为自己，消息为私密信息
                return self.decrypt_content(MODE_KEY_IV, message.content)
            else:
                return self.decrypt_content(MODE_KEY_KEY, message.content)
        else:
            if message.receiver == self.address:
                return self.decrypt_content(MODE_KEY_KEY, message.content, message.ekey)
        return None

    def is_mine(self, message):
        """检测信息是否是自己的信息"""
        if message.sender == self.address and message.receiver != PUBLIC_ADDRESS:
            return True
        if message.receiver == self.address:
            return True
        return False

    def message_type(self, message):
        """获取信息类型"""
        if self.is_mine(message):
            return 1
        elif message.receiver == PUBLIC_ADDRESS:
            return 2
        else:
            return 0

    def encrypt_content(self, mode, content):
        """加密内容
        Args:
            mode: 加密模式
            content: 明文
        Return:
            encrypted_key: 加密后的文本
        """
        if mode == MODE_KEY_KEY:
            key = binascii.unhexlify(self.__aes_key)
            iv = binascii.unhexlify(self.__aes_key)
        elif mode == MODE_KEY_IV:
            key = binascii.unhexlify(self.__aes_key)
            iv = binascii.unhexlify(self.__aes_iv)
        elif mode == MODE_NONE:
            return binascii.hexlify(content.encode('utf-8')).decode('utf-8')
        else:
            return content
        cipher = AES.new(key, AES.MODE_CFB, iv)
        encrypt = cipher.encrypt(content.encode('utf-8'))
        readable_encrypt = binascii.hexlify(encrypt).decode('utf-8')
        return readable_encrypt

    def decrypt_content(self, mode, encrypted_content, ekey=None):
        """解密内容
        Args:
            mode: 加密模式
            encrypted_content: 密文
            ekey: 加密的AES密钥
        Return:
            content: 明文
        """
        if mode == MODE_KEY_IV:
            key = binascii.unhexlify(self.__aes_key)
            iv = binascii.unhexlify(self.__aes_iv)
        elif mode == MODE_KEY_KEY and ekey is not None:
            # 解密AES密钥
            key = binascii.unhexlify(self.decrypt_aes_key(ekey))
            iv = key
        elif mode == MODE_KEY_KEY and ekey is None:
            # 使用自己的AES密钥解密
            key = binascii.unhexlify(self.__aes_key)
            iv = key
        elif mode == MODE_NONE:
            return binascii.unhexlify(encrypted_content).decode('utf-8')
        else:
            return None
        encrypt = binascii.unhexlify(encrypted_content)
        cipher = AES.new(key, AES.MODE_CFB, iv)
        decrypt = cipher.decrypt(encrypt)
        readable_decrypt = decrypt.decode('utf-8')
        return readable_decrypt

    def encrypt_aes_key(self, rsa_pubkey):
        """使用RSA公钥加密AES密钥
        Args:
            rsa_pubkey: rsa公钥
        Return:
            encrypted_key: 加密后的AES密钥
        """
        h = SHA.new(self.__aes_key.encode('utf-8'))
        key = RSA.importKey(rsa_pubkey)
        cipher = PKCS1_v1_5.new(key)
        encrypt = cipher.encrypt(self.__aes_key.encode('utf-8') + h.digest())
        readable_encrypt = binascii.hexlify(encrypt).decode('utf-8')
        return readable_encrypt

    def decrypt_aes_key(self, encrypted_key):
        """解码AES密钥
        Args:
            encrypted_key: 加密后的AES密钥
        Return:
            aes_key: 成功解密返回解密后的AES密钥, 失败返回None
        """
        encrypt = binascii.unhexlify(encrypted_key)
        key = RSA.importKey(self.__rsa_prikey)
        dsize = SHA.digest_size
        sentinel = Random.new().read(15 + dsize)  # Let's assume that average data length is 15
        cipher = PKCS1_v1_5.new(key)
        decrypt = cipher.decrypt(encrypt, sentinel)
        digest = SHA.new(decrypt[:-dsize]).digest()
        if digest == decrypt[-dsize:]:
            aes_key = decrypt[:-dsize].decode('utf-8')
        else:
            aes_key = None
        return aes_key


def verify_message(message):
    """验证信息有效性"""
    # 验证公钥
    if message.sender != pubkey2address(message.pubkey):
        return False
    # 验证签名
    ecc_pubkey = PublicKey(bytes(bytearray.fromhex(message.pubkey)), raw=True)
    # print(ecc_pubkey)
    sign = ecc_pubkey.ecdsa_deserialize(binascii.unhexlify(message.sign))
    verified = ecc_pubkey.ecdsa_verify(binascii.unhexlify(message.content), sign)
    # print(verified)
    return verified


# 文本加密模式
MODE_KEY_KEY = 1  # 用于对话信息，使用key作为初始向量
MODE_KEY_IV = 2  # 用于私密信息，使用iv未作初始向量
MODE_NONE = 3  # 不加密信息
# 公开信息地址
PUBLIC_ADDRESS = "0"
