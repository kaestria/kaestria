import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from kernel.system.Constant import VISTRO_HOME, VISTRO_USERS, VISTRO_ROOT, PROFILE_FILE, ADMIN_USER, HASH_ALGORITHM
import json
import hashlib
def hashPassword(password: str) -> str:
    return hashlib.new(HASH_ALGORITHM, password.encode()).hexdigest()
class Session:
    def __init__(self):
        self.username = ADMIN_USER
        self.role = "admin"
        self.currentPath = VISTRO_ROOT
        self._pendingSudo = None
        self._pendingUninstall = None
        self._activeShells = {}
    def getUsername(self) -> str:
        return self.username
    def getRole(self) -> str:
        return self.role
    def getCurrentPath(self) -> Path:
        return self.currentPath
    def setCurrentPath(self, path: Path):
        self.currentPath = path
    def getPrompt(self) -> str:
        try:
            rel = self.currentPath.relative_to(VISTRO_ROOT.parent.parent)
            display = "~/" + str(rel).replace("\\", "/")
        except ValueError:
            display = str(self.currentPath)
        return f"{self.username}@vistro:{display}> "
    def isAdmin(self) -> bool:
        return self.role == "admin"
    def setPendingSudo(self, programName: str, content: str, args: list):
        self._pendingSudo = {"programName": programName, "content": content, "args": args}
    def getPendingSudo(self):
        return self._pendingSudo
    def clearPendingSudo(self):
        self._pendingSudo = None
    def setPendingUninstall(self, appName: str):
        self._pendingUninstall = {"appName": appName}
    def getPendingUninstall(self):
        return self._pendingUninstall
    def clearPendingUninstall(self):
        self._pendingUninstall = None
    def addShell(self, name: str, info: dict):
        self._activeShells[name] = info
    def removeShell(self, name: str):
        if name in self._activeShells:
            del self._activeShells[name]
    def listShells(self) -> list:
        return sorted(self._activeShells.keys())
    def getShell(self, name: str):
        return self._activeShells.get(name)
    def clearShells(self):
        self._activeShells = {}
