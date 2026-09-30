from pathlib import Path
class FsModule:
    @staticmethod
    def joinPaths(a, b):
        return str(Path(str(a or "")) / str(b or ""))
    @staticmethod
    def baseName(p):
        return Path(str(p or "")).name
    @staticmethod
    def dirName(p):
        return str(Path(str(p or "")).parent)
    @staticmethod
    def readLineContent(content: str, idx):
        try:
            lines = str(content or "").splitlines()
            i = int(idx or 0)
            return lines[i] if 0 <= i < len(lines) else None
        except Exception:
            return None
    @staticmethod
    def getLength(content: str):
        try:
            return len(str(content or ""))
        except Exception:
            return 0
    @staticmethod
    def listNames(entries: list):
        try:
            return "\n".join([str(e) for e in (entries or [])])
        except Exception:
            return ""
    @staticmethod
    def statInfo(path, isDir: bool, size: int, mtime: float):
        try:
            import json
            return json.dumps({"path": str(path or ""), "isDir": bool(isDir), "size": int(size or 0), "mtime": float(mtime or 0)})
        except Exception:
            return ""
