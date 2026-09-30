import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from kernel.system.Constant import VISTRO_ROOT
from fs.Sandbox import isInsideSandbox
class FileSystem:
    def __init__(self, basePath: Path = None):
        self.basePath = basePath or VISTRO_ROOT
    def getBasePath(self) -> Path:
        return self.basePath
    def setBasePath(self, path: Path):
        self.basePath = path
    def readText(self, path: Path) -> str | None:
        try:
            if path.exists() and path.is_file():
                return path.read_text(encoding="utf-8")
            return None
        except Exception:
            return None
    def writeText(self, path: Path, content: str) -> bool:
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(str(content or ""), encoding="utf-8")
            return True
        except Exception:
            return False
    def appendText(self, path: Path, content: str) -> bool:
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "a", encoding="utf-8") as f:
                f.write(str(content or ""))
            return True
        except Exception:
            return False
    def readLine(self, path: Path, lineNumber: int) -> str | None:
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
            if 0 <= lineNumber < len(lines):
                return lines[lineNumber]
            return None
        except Exception:
            return None
    def readLines(self, path: Path) -> list:
        try:
            return path.read_text(encoding="utf-8").splitlines()
        except Exception:
            return []
    def getLineCount(self, path: Path) -> int:
        try:
            return len(path.read_text(encoding="utf-8").splitlines())
        except Exception:
            return 0
    def getLength(self, path: Path) -> int:
        try:
            return len(path.read_text(encoding="utf-8"))
        except Exception:
            return 0
    def exists(self, path: Path) -> bool:
        try:
            return path.exists()
        except Exception:
            return False
    def delete(self, path: Path) -> bool:
        try:
            if path.is_dir():
                import shutil
                shutil.rmtree(path)
            elif path.exists():
                path.unlink()
            return True
        except Exception:
            return False
    def listFiles(self, path: Path) -> list:
        try:
            if path.is_dir():
                return [p.name for p in path.iterdir()]
            return []
        except Exception:
            return []
