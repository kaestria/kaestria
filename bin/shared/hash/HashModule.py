import hashlib
class HashModule:
    @staticmethod
    def hashText(v):
        try:
            return hashlib.sha256(str(v or "").encode()).hexdigest()
        except Exception:
            return ""
    @staticmethod
    def hashSha256(v):
        try:
            return hashlib.sha256(str(v or "").encode()).hexdigest()
        except Exception:
            return ""
    @staticmethod
    def hashMd5(v):
        try:
            return hashlib.md5(str(v or "").encode()).hexdigest()
        except Exception:
            return ""
