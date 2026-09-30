import random
import string
class RandomModule:
    @staticmethod
    def randomInt(a, b):
        try:
            lo = int(a or 0)
            hi = int(b or 0)
            if lo > hi:
                lo, hi = hi, lo
            return random.randint(lo, hi)
        except Exception:
            return 0
    @staticmethod
    def randomString(length, charset):
        try:
            n = int(length or 0)
            chars = str(charset or "")
            if not chars:
                chars = string.ascii_letters + string.digits
            return "".join(random.choice(chars) for _ in range(max(n, 0)))
        except Exception:
            return ""
    @staticmethod
    def randomChoice(lst):
        try:
            l = lst if isinstance(lst, list) else []
            if not l:
                return None
            return random.choice(l)
        except Exception:
            return None
