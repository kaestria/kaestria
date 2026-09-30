import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from kernel.system.Constant import VISTRO_ROOT
from fs.Sandbox import isInsideSandbox, resolvePath
class PathSystem:
    def __init__(self, currentPath: Path = None):
        self.currentPath = currentPath or VISTRO_ROOT
    def getCurrentPath(self) -> Path:
        return self.currentPath
    def setCurrentPath(self, path: Path):
        self.currentPath = path
    def joinPath(self, base: str, other: str) -> Path:
        return (Path(base) / other)
    def getBaseName(self, path: Path) -> str:
        return Path(path).name
    def getDirName(self, path: Path) -> str:
        return str(Path(path).parent)
    def getSuffix(self, path: Path) -> str:
        return Path(path).suffix
    def getStem(self, path: Path) -> str:
        return Path(path).stem
    def isAbsolute(self, path: str) -> bool:
        return Path(path).is_absolute()
    def normalize(self, path: Path) -> Path:
        return Path(path).resolve()
    def getRelative(self, path: Path, base: Path) -> Path | None:
        try:
            return Path(path).resolve().relative_to(Path(base).resolve())
        except ValueError:
            return None
    def toDisplay(self, path: Path) -> str:
        try:
            rel = Path(path).resolve().relative_to(VISTRO_ROOT.parent.parent.resolve())
            return "~/" + str(rel).replace("\\", "/")
        except ValueError:
            return str(path)
    def resolve(self, target: str) -> Path:
        return resolvePath(self.currentPath, target)
    def isSandboxPath(self, path: Path) -> bool:
        return isInsideSandbox(path)
    def splitParts(self, path: Path) -> tuple:
        return Path(path).parts
    def parentPath(self, path: Path) -> Path:
        return Path(path).parent
