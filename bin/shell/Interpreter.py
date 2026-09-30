import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from bin.shared.Interpreter import SharedInterpreter
from bin.shared.Language import OPCODE_FUNC, OPCODE_ENDFUNC, OPCODE_IF, OPCODE_WHILE, OPCODE_VAR_STR, OPCODE_VAR_INT, OPCODE_VAR_BOOL, OPCODE_SET
from bin.shell.Language import OPCODE_LOGIN, OPCODE_LOGOUT, OPCODE_TOKENSET, OPCODE_TOKENCLEAR, OPCODE_TOKENUSER, OPCODE_INPUT, OPCODE_WINCREATE, OPCODE_WINSET, OPCODE_WINCLOSE, OPCODE_UICREATE, OPCODE_UISET, OPCODE_UIGET, OPCODE_UION, OPCODE_UIBLUR, OPCODE_UICURSOR, OPCODE_UISOUND, OPCODE_UIWEB, OPCODE_UICLEAR
from bin.shell.session import Session as ShellSession
class ShellInterpreter(SharedInterpreter):
    def __init__(self, shellName: str = "", modules: dict = None, vistroRoot: Path = None, shellArgs: list = None, username: str = None, role: str = None):
        super().__init__(programName=None, isSudo=False, vistroRoot=vistroRoot, username=username, role=role)
        self.shellName = str(shellName or "")
        self.modules = dict(modules or {})
        self.shellToken = None
        self.windows = {}
        self.elements = {}
        self.nextWindow = 1
        self.nextElement = 1
        self.inputQueue = list(shellArgs or [])
        self.cursor = "default"
        self.sounds = []
    def setInputQueue(self, items: list):
        self.inputQueue = list(items or [])
    def getImportBytecode(self, name: str):
        try:
            key = str(name or "").strip()
            if key in self.modules:
                return self.modules[key]
            alt = key.replace("/", ".")
            if alt in self.modules:
                return self.modules[alt]
        except Exception:
            pass
        return None
    def importModule(self, name: str) -> bool:
        key = str(name or "").strip()
        if not key or "/" in key or "\\" in key or ".." in key:
            return False
        bytecode = self.getImportBytecode(key)
        if not bytecode:
            return False
        sub = SharedInterpreter(vistroRoot=self.vistroRoot, username=self.username, role=self.role)
        sub.functions = {}
        sub._scanFunctions(bytecode)
        self.functions.update(sub.functions)
        pos = 0
        end = len(bytecode)
        while pos < end:
            op = bytecode[pos]
            pos += 1
            if op == OPCODE_FUNC:
                _, pos = self._readToken(bytecode, pos)
                depth = 1
                while pos < end and depth > 0:
                    inner = bytecode[pos]
                    pos += 1
                    if inner == OPCODE_FUNC:
                        _, pos = self._readToken(bytecode, pos)
                        depth += 1
                    elif inner == OPCODE_ENDFUNC:
                        depth -= 1
                    else:
                        pos = self._skipInstruction(bytecode, pos, inner)
            elif op == OPCODE_IF:
                pos = self._skipValue(bytecode, pos)
                pos = self._findMatchingEndif(bytecode, pos, end)
            elif op == OPCODE_WHILE:
                pos = self._skipValue(bytecode, pos)
                pos = self._findMatchingEndWhile(bytecode, pos, end)
            elif op in (OPCODE_VAR_STR, OPCODE_VAR_INT, OPCODE_VAR_BOOL, OPCODE_SET):
                varName, pos = self._readToken(bytecode, pos)
                val, pos = self._readValue(bytecode, pos)
                if op == OPCODE_VAR_STR:
                    self.vars[varName] = str(val) if val is not None else ""
                elif op == OPCODE_VAR_INT:
                    try:
                        self.vars[varName] = int(val) if val is not None else 0
                    except Exception:
                        self.vars[varName] = 0
                elif op == OPCODE_VAR_BOOL:
                    self.vars[varName] = bool(val) if val is not None else False
                else:
                    self.vars[varName] = val
            else:
                pos = self._skipInstruction(bytecode, pos, op)
        return True
    def _sandboxPath(self, path: str) -> Path:
        from fs.Sandbox import canAccess
        shellBase = self.vistroRoot / "shell"
        base = shellBase / self.shellName if self.shellName else shellBase
        tokenData = ShellSession.validateToken(self.shellToken) if self.shellToken else None
        p = Path(str(path or ""))
        if not p.is_absolute():
            p = base / p
        resolved = p.resolve()
        try:
            resolved.relative_to(base.resolve())
            return resolved
        except ValueError:
            pass
        if tokenData is None:
            raise PermissionError(f"Access denied: {path}")
        try:
            resolved.relative_to(self.vistroRoot.resolve())
        except ValueError:
            raise PermissionError(f"Access denied: {path}")
        username = tokenData.get("username", "")
        role = tokenData.get("role", "user")
        if not canAccess(resolved, username, role):
            raise PermissionError(f"Access denied: {path}")
        return resolved
    def checkManualGuard(self, path: Path, write: bool = True):
        from fs.Sandbox import isProtectedManualPath
        from kernel.system.Constant import PROFILE_FILE
        if isProtectedManualPath(path):
            raise PermissionError("protected path")
        if path.name == PROFILE_FILE:
            raise PermissionError("protected file")
    def skipExtension(self, opcode: int, data: bytes, pos: int):
        try:
            if opcode == OPCODE_TOKENCLEAR:
                return pos
            if opcode in (OPCODE_LOGOUT, OPCODE_TOKENSET, OPCODE_WINCLOSE, OPCODE_UICURSOR, OPCODE_UISOUND, OPCODE_UICLEAR):
                return self._skipValue(data, pos)
            if opcode in (OPCODE_TOKENUSER, OPCODE_INPUT, OPCODE_WINCREATE):
                _, pos = self._readToken(data, pos)
                pos = self._skipValue(data, pos)
                return pos
            if opcode in (OPCODE_LOGIN, OPCODE_UICREATE, OPCODE_UIWEB, OPCODE_UIBLUR, OPCODE_UIGET):
                _, pos = self._readToken(data, pos)
                pos = self._skipValue(data, pos)
                pos = self._skipValue(data, pos)
                return pos
            if opcode in (OPCODE_WINSET, OPCODE_UISET, OPCODE_UION):
                pos = self._skipValue(data, pos)
                pos = self._skipValue(data, pos)
                pos = self._skipValue(data, pos)
                return pos
        except Exception:
            pass
        return None
    def handleExtension(self, opcode: int, data: bytes, pos: int, end: int, executing: bool):
        if opcode == OPCODE_LOGIN:
            dest, pos = self._readToken(data, pos)
            user, pos = self._readValue(data, pos)
            pwd, pos = self._readValue(data, pos)
            if executing:
                result = ShellSession.loginUser(user, pwd, self.shellName)
                self.vars[dest] = result
                if result != -1:
                    self.shellToken = result
            return pos
        if opcode == OPCODE_LOGOUT:
            val, pos = self._readValue(data, pos)
            if executing:
                ShellSession.logoutToken(val)
                if val == self.shellToken:
                    self.shellToken = None
            return pos
        if opcode == OPCODE_TOKENSET:
            val, pos = self._readValue(data, pos)
            if executing:
                tokenData = ShellSession.validateToken(val)
                if tokenData:
                    self.shellToken = str(val)
                else:
                    self._print("[ERR] invalid token")
            return pos
        if opcode == OPCODE_TOKENCLEAR:
            if executing:
                self.shellToken = None
            return pos
        if opcode == OPCODE_TOKENUSER:
            dest, pos = self._readToken(data, pos)
            val, pos = self._readValue(data, pos)
            if executing:
                self.vars[dest] = ShellSession.tokenUser(val)
            return pos
        if opcode == OPCODE_INPUT:
            dest, pos = self._readToken(data, pos)
            prompt, pos = self._readValue(data, pos)
            if executing:
                if prompt:
                    self._print(str(prompt))
                if self.inputQueue:
                    self.vars[dest] = self.inputQueue.pop(0)
                else:
                    self.vars[dest] = ""
            return pos
        if opcode == OPCODE_WINCREATE:
            dest, pos = self._readToken(data, pos)
            title, pos = self._readValue(data, pos)
            if executing:
                wid = f"win{self.nextWindow}"
                self.nextWindow += 1
                self.windows[wid] = {"title": str(title or ""), "width": 800, "height": 600, "x": 0, "y": 0, "visible": True}
                self.vars[dest] = wid
            return pos
        if opcode == OPCODE_WINSET:
            win, pos = self._readValue(data, pos)
            prop, pos = self._readValue(data, pos)
            val, pos = self._readValue(data, pos)
            if executing:
                wid = str(win or "")
                if wid in self.windows:
                    self.windows[wid][str(prop or "")] = val
            return pos
        if opcode == OPCODE_WINCLOSE:
            val, pos = self._readValue(data, pos)
            if executing:
                wid = str(val or "")
                if wid in self.windows:
                    del self.windows[wid]
            return pos
        if opcode == OPCODE_UICREATE:
            dest, pos = self._readToken(data, pos)
            utype, pos = self._readValue(data, pos)
            parent, pos = self._readValue(data, pos)
            if executing:
                eid = f"ui{self.nextElement}"
                self.nextElement += 1
                self.elements[eid] = {"type": str(utype or ""), "parent": str(parent or ""), "props": {}}
                self.vars[dest] = eid
            return pos
        if opcode == OPCODE_UISET:
            elem, pos = self._readValue(data, pos)
            prop, pos = self._readValue(data, pos)
            val, pos = self._readValue(data, pos)
            if executing:
                eid = str(elem or "")
                if eid in self.elements:
                    self.elements[eid]["props"][str(prop or "")] = val
            return pos
        if opcode == OPCODE_UIGET:
            dest, pos = self._readToken(data, pos)
            elem, pos = self._readValue(data, pos)
            prop, pos = self._readValue(data, pos)
            if executing:
                eid = str(elem or "")
                if eid in self.elements:
                    self.vars[dest] = self.elements[eid]["props"].get(str(prop or ""), None)
                elif eid in self.windows:
                    self.vars[dest] = self.windows[eid].get(str(prop or ""), None)
                else:
                    self.vars[dest] = None
            return pos
        if opcode == OPCODE_UION:
            elem, pos = self._readValue(data, pos)
            event, pos = self._readValue(data, pos)
            func, pos = self._readValue(data, pos)
            if executing:
                eid = str(elem or "")
                if eid in self.elements:
                    self.elements[eid]["props"][f"on_{event}"] = str(func or "")
            return pos
        if opcode == OPCODE_UIBLUR:
            dest, pos = self._readToken(data, pos)
            target, pos = self._readValue(data, pos)
            radius, pos = self._readValue(data, pos)
            if executing:
                try:
                    r = int(radius or 0)
                except Exception:
                    r = 0
                eid = f"ui{self.nextElement}"
                self.nextElement += 1
                self.elements[eid] = {"type": "blur", "parent": str(target or ""), "props": {"radius": r, "cornerradius": 0}}
                self.vars[dest] = eid
            return pos
        if opcode == OPCODE_UICURSOR:
            val, pos = self._readValue(data, pos)
            if executing:
                self.cursor = str(val or "default")
            return pos
        if opcode == OPCODE_UISOUND:
            val, pos = self._readValue(data, pos)
            if executing:
                self.sounds.append(str(val or ""))
            return pos
        if opcode == OPCODE_UIWEB:
            dest, pos = self._readToken(data, pos)
            url, pos = self._readValue(data, pos)
            parent, pos = self._readValue(data, pos)
            if executing:
                eid = f"ui{self.nextElement}"
                self.nextElement += 1
                self.elements[eid] = {"type": "webview", "parent": str(parent or ""), "props": {"url": str(url or "")}}
                self.vars[dest] = eid
            return pos
        if opcode == OPCODE_UICLEAR:
            val, pos = self._readValue(data, pos)
            if executing:
                wid = str(val or "")
                doomed = [k for k, v in self.elements.items() if v.get("parent") == wid]
                for k in doomed:
                    del self.elements[k]
            return pos
        return None
