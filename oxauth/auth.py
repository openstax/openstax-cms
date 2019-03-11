import json
import base64
import urllib
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2


class OXSessionDecryptor(object):
    def __init__(self, secret_key_base, salt="encrypted cookie", keylen=64, iterations=1000):
        self.secret = PBKDF2(secret_key_base, salt.encode(), keylen, iterations)

    def get_cookie_data(self, cookie):
        cookie = base64.b64decode(urllib.parse.unquote(cookie).split('--')[0])
        encrypted_data, iv = map(base64.b64decode, cookie.split('--'.encode()))
        cipher = AES.new(self.secret[:32], AES.MODE_CBC, iv)
        return json.loads(unpad(cipher.decrypt(encrypted_data)))