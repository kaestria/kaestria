from datetime import date
class DataModule:
    @staticmethod
    def getDate():
        return date.today().isoformat()
    @staticmethod
    def getDateDmy():
        t = date.today()
        return f"{t.day:02d}/{t.month:02d}/{t.year:04d}"
    @staticmethod
    def getWeekday():
        return date.today().isoweekday()
    @staticmethod
    def getDayOfYear():
        return date.today().timetuple().tm_yday
    @staticmethod
    def getMonth():
        return date.today().month
    @staticmethod
    def getYear():
        return date.today().year
    @staticmethod
    def getDay():
        return date.today().day
