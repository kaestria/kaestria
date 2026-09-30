from datetime import datetime
import time
class TimeModule:
    @staticmethod
    def getTime():
        return datetime.now().strftime("%H:%M:%S")
    @staticmethod
    def getHour():
        return datetime.now().hour
    @staticmethod
    def getMinute():
        return datetime.now().minute
    @staticmethod
    def getSecond():
        return datetime.now().second
    @staticmethod
    def getTimestamp():
        return int(time.time())
