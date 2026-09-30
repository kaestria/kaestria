import hashlib
import base64
class EncryptModule:
    @staticmethod
    def encryptText(v, key):
        try:
            data = str(v or "").encode()
            k = hashlib.sha256(str(key or "").encode()).digest()
            enc = bytes([b ^ k[i % len(k)] for i, b in enumerate(data)])
            return base64.b64encode(enc).decode()
        except Exception:
            return ""
    @staticmethod
    def decryptText(v, key):
        try:
            raw = base64.b64decode(str(v or "").encode())
            k = hashlib.sha256(str(key or "").encode()).digest()
            dec = bytes([b ^ k[i % len(k)] for i, b in enumerate(raw)])
            return dec.decode()
        except Exception:
            return ""
