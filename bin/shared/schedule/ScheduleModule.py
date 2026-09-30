import time
class ScheduleModule:
    @staticmethod
    def sleepSeconds(v):
        try:
            time.sleep(float(v or 0))
        except Exception:
            pass
    @staticmethod
    def getFps():
        return 60
    @staticmethod
    def getTick():
        try:
            return int(time.time() * 60)
        except Exception:
            return 0
