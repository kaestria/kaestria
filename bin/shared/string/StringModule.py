class StringModule:
    @staticmethod
    def isString(v):
        return isinstance(v, str)
    @staticmethod
    def findText(haystack, needle):
        try:
            return str(haystack or "").find(str(needle or ""))
        except Exception:
            return -1
    @staticmethod
    def replaceText(src, old, new):
        try:
            return str(src or "").replace(str(old or ""), str(new or ""))
        except Exception:
            return str(src or "")
    @staticmethod
    def trimText(v):
        try:
            return str(v or "").strip()
        except Exception:
            return ""
    @staticmethod
    def startsWith(src, prefix):
        try:
            return str(src or "").startswith(str(prefix or ""))
        except Exception:
            return False
    @staticmethod
    def endsWith(src, suffix):
        try:
            return str(src or "").endswith(str(suffix or ""))
        except Exception:
            return False
    @staticmethod
    def reverseText(v):
        try:
            return str(v or "")[::-1]
        except Exception:
            return ""
    @staticmethod
    def joinTexts(lst, sep):
        try:
            l = lst if isinstance(lst, list) else []
            return str(sep or "").join([str(x) for x in l])
        except Exception:
            return ""
    @staticmethod
    def charAt(src, idx):
        try:
            s = str(src or "")
            i = int(idx or 0)
            return s[i] if 0 <= i < len(s) else ""
        except Exception:
            return ""
    @staticmethod
    def toUpper(v):
        return str(v or "").upper()
    @staticmethod
    def toLower(v):
        return str(v or "").lower()
    @staticmethod
    def getLength(v):
        return len(str(v or ""))
    @staticmethod
    def splitText(s, sep):
        try:
            return str(s or "").split(str(sep or " "))
        except Exception:
            return []
    @staticmethod
    def padText(src, width, padChar):
        try:
            s = str(src or "")
            w = int(width or 0)
            c = str(padChar or " ")
            if not c:
                c = " "
            return s.rjust(w, c[0])
        except Exception:
            return str(src or "")
    @staticmethod
    def repeatText(src, count):
        try:
            return str(src or "") * max(int(count or 0), 0)
        except Exception:
            return ""
    @staticmethod
    def countText(haystack, needle):
        try:
            return str(haystack or "").count(str(needle or ""))
        except Exception:
            return 0
    @staticmethod
    def cmpText(a, b):
        try:
            return str(a or "").lower() == str(b or "").lower()
        except Exception:
            return False
    @staticmethod
    def sliceText(src, start, end):
        try:
            s = str(src or "")
            st = int(start or 0)
            en = int(end if end is not None else len(s))
            return s[st:en]
        except Exception:
            return ""
