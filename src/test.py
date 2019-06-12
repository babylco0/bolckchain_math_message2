from MMMessage import *
from MMUser import *
import json

msg = MMMessage()
msg.sender = '1'
msg.receiver = '2'
msg.content = '3'
msg.time = '4'
msg.sign = '5'
msg.pubkey = '6'
msg.ekey = '7'
str_msg = msg.serialize()
print(str_msg)
msg2 = MMMessage(json.loads(str_msg))
print(msg2.serialize())
user = MMUser(u_name='Alice', u_path='demo_users.json')
user.load_keys()
print(user.rsa_prikey)
msg = user.create_chat_message(user.address, user.rsa_pubkey, 'hello world')
print(msg.serialize())
if verify_message(msg):
    print(user.decode_message(msg))
msg = user.create_public_message('hello world')
print(msg.serialize())
if verify_message(msg):
    print(user.decode_message(msg))
msg = user.create_private_message('hello world')
print(msg.serialize())
if verify_message(msg):
    print(user.decode_message(msg))

print(user.address)