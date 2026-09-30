import uuid
class UuidModule:
    @staticmethod
    def newUuid():
        try:
            return str(uuid.uuid4())
        except Exception:
            return ""
