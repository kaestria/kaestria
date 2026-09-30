class LoggerModule:
    @staticmethod
    def formatInfo(msg):
        return f"{msg if msg is not None else ''}"
    @staticmethod
    def formatWarn(msg):
        return f"{msg if msg is not None else ''}"
    @staticmethod
    def formatError(msg):
        return f"{msg if msg is not None else ''}"