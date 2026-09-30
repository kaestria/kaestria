import math
class MathModule:
    @staticmethod
    def roundValue(v):
        try:
            return round(float(v or 0))
        except Exception:
            return 0
    @staticmethod
    def floorValue(v):
        try:
            return math.floor(float(v or 0))
        except Exception:
            return 0
    @staticmethod
    def ceilValue(v):
        try:
            return math.ceil(float(v or 0))
        except Exception:
            return 0
    @staticmethod
    def sqrtValue(v):
        try:
            fv = float(v or 0)
            return fv ** 0.5 if fv >= 0 else 0
        except Exception:
            return 0
    @staticmethod
    def powValue(a, b):
        try:
            return (float(a or 0)) ** (float(b or 0))
        except Exception:
            return 0
    @staticmethod
    def absValue(v):
        try:
            fv = float(v or 0)
            av = abs(fv)
            return int(av) if float(int(av)) == av else av
        except Exception:
            return 0
    @staticmethod
    def isOdd(v):
        try:
            return int(float(v or 0)) % 2 == 1
        except Exception:
            return False
    @staticmethod
    def isEven(v):
        try:
            return int(float(v or 0)) % 2 == 0
        except Exception:
            return False
    @staticmethod
    def fdivValue(a, b):
        try:
            bv = float(b or 0)
            return float(a or 0) / bv if bv != 0 else 0
        except Exception:
            return 0
    @staticmethod
    def minValue(a, b):
        try:
            fa = float(a or 0)
            fb = float(b or 0)
            m = fa if fa < fb else fb
            return int(m) if float(int(m)) == m else m
        except Exception:
            return 0
    @staticmethod
    def maxValue(a, b):
        try:
            fa = float(a or 0)
            fb = float(b or 0)
            m = fa if fa > fb else fb
            return int(m) if float(int(m)) == m else m
        except Exception:
            return 0
