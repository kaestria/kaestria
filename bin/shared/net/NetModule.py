import socket
import urllib.request
import urllib.parse
class NetModule:
    @staticmethod
    def getNetInfo():
        try:
            return socket.gethostname()
        except Exception:
            return "localhost"
    @staticmethod
    def parseHeaders(raw):
        try:
            import json
            if raw is None or raw == "":
                return {}
            if isinstance(raw, dict):
                return {str(k): str(v) for k, v in raw.items()}
            data = json.loads(str(raw))
            if isinstance(data, dict):
                return {str(k): str(v) for k, v in data.items()}
            return {}
        except Exception:
            return {}
    @staticmethod
    def httpGet(url, headers, timeout):
        try:
            req = urllib.request.Request(str(url or ""), headers=NetModule.parseHeaders(headers), method="GET")
            with urllib.request.urlopen(req, timeout=float(timeout or 10)) as resp:
                return resp.read().decode("utf-8", errors="replace")
        except Exception:
            return None
    @staticmethod
    def httpPost(url, body, headers, timeout):
        try:
            data = str(body or "").encode("utf-8")
            req = urllib.request.Request(str(url or ""), data=data, headers=NetModule.parseHeaders(headers), method="POST")
            with urllib.request.urlopen(req, timeout=float(timeout or 10)) as resp:
                return resp.read().decode("utf-8", errors="replace")
        except Exception:
            return None
    @staticmethod
    def httpStatus(url, timeout):
        try:
            req = urllib.request.Request(str(url or ""), method="GET")
            with urllib.request.urlopen(req, timeout=float(timeout or 10)) as resp:
                return int(resp.status)
        except Exception as e:
            try:
                if hasattr(e, "code"):
                    return int(e.code)
            except Exception:
                pass
            return -1
    @staticmethod
    def urlEncodeText(v):
        try:
            return urllib.parse.quote(str(v or ""), safe="")
        except Exception:
            return ""
    @staticmethod
    def urlDecodeText(v):
        try:
            return urllib.parse.unquote(str(v or ""))
        except Exception:
            return ""
