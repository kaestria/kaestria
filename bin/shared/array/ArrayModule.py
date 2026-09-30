class ArrayModule:
    @staticmethod
    def createArray(items):
        return list(items or [])
    @staticmethod
    def getItem(lst, idx):
        try:
            l = lst if isinstance(lst, list) else []
            i = int(idx or 0)
            return l[i] if 0 <= i < len(l) else None
        except Exception:
            return None
    @staticmethod
    def setItem(lst, idx, value):
        try:
            l = list(lst) if isinstance(lst, list) else []
            i = int(idx or 0)
            if 0 <= i < len(l):
                l[i] = value
            return l
        except Exception:
            return lst
    @staticmethod
    def removeItem(lst, idx):
        try:
            l = list(lst) if isinstance(lst, list) else []
            i = int(idx or 0)
            if 0 <= i < len(l):
                l.pop(i)
            return l
        except Exception:
            return lst
    @staticmethod
    def containsValue(lst, value):
        try:
            return value in (lst if isinstance(lst, list) else [])
        except Exception:
            return False
    @staticmethod
    def joinValues(lst, sep):
        try:
            l = lst if isinstance(lst, list) else []
            return str(sep or "").join([str(x) for x in l])
        except Exception:
            return ""
    @staticmethod
    def sortValues(lst):
        try:
            l = list(lst) if isinstance(lst, list) else []
            return sorted(l, key=lambda x: str(x))
        except Exception:
            return []
    @staticmethod
    def reverseValues(lst):
        try:
            l = list(lst) if isinstance(lst, list) else []
            l.reverse()
            return l
        except Exception:
            return []
    @staticmethod
    def sliceValues(lst, start, end):
        try:
            l = list(lst) if isinstance(lst, list) else []
            st = int(start or 0)
            en = int(end if end is not None else len(l))
            return l[st:en]
        except Exception:
            return []
    @staticmethod
    def indexOf(lst, value):
        try:
            l = lst if isinstance(lst, list) else []
            return l.index(value)
        except Exception:
            return -1
    @staticmethod
    def uniqueValues(lst):
        try:
            out = []
            for x in (lst if isinstance(lst, list) else []):
                if x not in out:
                    out.append(x)
            return out
        except Exception:
            return []
    @staticmethod
    def rangeValues(start, end):
        try:
            return list(range(int(start or 0), int(end or 0)))
        except Exception:
            return []
