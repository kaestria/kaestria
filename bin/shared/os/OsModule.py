import platform
import locale
import socket
class OsModule:
    @staticmethod
    def getOsName():
        try:
            return f"{platform.system()} {platform.machine()}"
        except Exception:
            return "Unknown"
    @staticmethod
    def getOsArch():
        try:
            return platform.machine()
        except Exception:
            return "Unknown"
    @staticmethod
    def getOsLang():
        try:
            loc = locale.getdefaultlocale()
            if loc and loc[0]:
                return loc[0]
            return "en_US"
        except Exception:
            return "en_US"
    @staticmethod
    def getHostName():
        try:
            return socket.gethostname()
        except Exception:
            return "localhost"
    @staticmethod
    def isWindows():
        try:
            return platform.system().lower() == "windows"
        except Exception:
            return False
    @staticmethod
    def isLinux():
        try:
            return platform.system().lower() == "linux"
        except Exception:
            return False
