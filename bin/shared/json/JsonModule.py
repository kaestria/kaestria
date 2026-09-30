import json
class JsonModule:
    @staticmethod
    def parseText(v):
        try:
            return json.loads(str(v or ""))
        except Exception:
            return None
    @staticmethod
    def stringifyValue(v):
        try:
            return json.dumps(v)
        except Exception:
            return ""
    @staticmethod
    def getField(data, key):
        try:
            if isinstance(data, str):
                data = json.loads(data)
            if isinstance(data, dict):
                return data.get(str(key))
            if isinstance(data, list):
                return data[int(key or 0)]
            return None
        except Exception:
            return None
    @staticmethod
    def setField(data, key, value):
        try:
            if isinstance(data, str):
                try:
                    data = json.loads(data)
                except Exception:
                    data = {}
            if isinstance(data, dict):
                data[str(key)] = value
                return json.dumps(data)
            if isinstance(data, list):
                data[int(key or 0)] = value
                return json.dumps(data)
            return json.dumps(data)
        except Exception:
            return ""
