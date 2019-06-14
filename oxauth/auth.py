import json
import base64
import urllib
import hmac
import hashlib

from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

class OXSessionDecryptor(object):
    def __init__(self, secret_key_base, encrypted_cookie_salt="encrypted cookie", encrypted_signed_cookie_salt="signed encrypted cookie", keylen=64, iterations=1000):
        encrypted_cookie_salt = encrypted_cookie_salt.encode()
        encrypted_signed_cookie_salt = encrypted_signed_cookie_salt.encode()

        self.secret = hashlib.pbkdf2_hmac('sha1', secret_key_base.encode(), encrypted_cookie_salt, iterations, keylen)[:32]
        self.signsecret = hashlib.pbkdf2_hmac('sha1', secret_key_base.encode(), encrypted_signed_cookie_salt, iterations, keylen)

    # TODO: Fix the validation, and run the validation function as well.
    # def validate_cookie(self, cookie):
    #     data, digest = cookie.split('--')
        
    #     myhmac = hmac.new(self.signsecret, digestmod=hashlib.sha1)
    #     myhmac.update(data.encode())
    #     decrypted_digest = myhmac.hexdigest()

    #     return hmac.compare_digest(digest, decrypted_digest)

    def get_cookie_data(self, cookie):

        try:
            cookie = base64.b64decode(urllib.parse.unquote(cookie).split("--")[0])
            encrypted_data, iv = map(base64.b64decode, cookie.split("--".encode()))

            cipher = AES.new(self.secret, AES.MODE_CBC, iv)

            pt = unpad(cipher.decrypt(encrypted_data), AES.block_size)

            try:
                return json.loads(pt.decode())
            except:
                return json.loads(pt)
            
        except Exception as e: 
            return {"err": "Cookie decryption failed.", "code": str(e)}