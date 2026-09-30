class IntModule:
    @staticmethod
    def isInteger(v):
        return isinstance(v, int) and not isinstance(v, bool)
    @staticmethod
    def parseInt(v):
        try:
            if isinstance(v, bool):
                return 1 if v else 0
            if isinstance(v, int):
                return v
            return int(str(v or "").strip())
        except Exception:
            return 0
    @staticmethod
    def toString(v):
        try:
            return str(v or 0)
        except Exception:
            return "0"
    @staticmethod
    def clampValue(v, lo, hi):
        try:
            fv = int(v or 0)
            a = int(lo or 0)
            b = int(hi or 0)
            if a > b:
                a, b = b, a
            return max(a, min(b, fv))
        except Exception:
            return 0
