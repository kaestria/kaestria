class CommandModule:
    @staticmethod
    def getLength(args: list) -> int:
        try:
            return len(args or [])
        except Exception:
            return 0
    @staticmethod
    def getArgument(args: list, index):
        try:
            i = int(index or 0)
            a = args or []
            return a[i] if 0 <= i < len(a) else None
        except Exception:
            return None
