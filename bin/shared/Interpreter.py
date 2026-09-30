import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import struct
import socket
import urllib.request
import subprocess
from bin.shared.Language import OPCODE_VAR_STR, OPCODE_VAR_INT, OPCODE_VAR_BOOL, OPCODE_SET, OPCODE_PRINT, OPCODE_PRINTLN, OPCODE_IF, OPCODE_ELIF, OPCODE_ELSE, OPCODE_ENDIF, OPCODE_WHILE, OPCODE_ENDWHILE, OPCODE_BREAK, OPCODE_CONTINUE, OPCODE_SIGNAL, OPCODE_EMIT, OPCODE_FUNC, OPCODE_ENDFUNC, OPCODE_CALL, OPCODE_RETURN, OPCODE_ROUND, OPCODE_FLOOR, OPCODE_CEIL, OPCODE_SQRT, OPCODE_POW, OPCODE_ABS, OPCODE_ISODD, OPCODE_ISEVEN, OPCODE_ADD, OPCODE_SUB, OPCODE_MUL, OPCODE_DIV, OPCODE_MOD, OPCODE_ISINT, OPCODE_INTPARSE, OPCODE_INTSTR, OPCODE_INTCLAMP, OPCODE_EQ, OPCODE_NEQ, OPCODE_LT, OPCODE_GT, OPCODE_LTE, OPCODE_GTE, OPCODE_AND, OPCODE_OR, OPCODE_NOT, OPCODE_STRIS, OPCODE_STRFIND, OPCODE_STRREPLACE, OPCODE_STRTRIM, OPCODE_STRSTARTS, OPCODE_STRENDS, OPCODE_STRREV, OPCODE_CONCAT, OPCODE_STRLEN, OPCODE_SUBSTR, OPCODE_UPPER, OPCODE_LOWER, OPCODE_SPLIT, OPCODE_STRJOIN, OPCODE_STRCHAR, OPCODE_LIST, OPCODE_LISTGET, OPCODE_LISTLEN, OPCODE_LISTAPPEND, OPCODE_LISTSET, OPCODE_LISTREMOVE, OPCODE_LISTCONTAINS, OPCODE_LISTJOIN, OPCODE_ARRCREATE, OPCODE_FOPEN, OPCODE_FREAD, OPCODE_FWRITE, OPCODE_FAPPEND, OPCODE_FDELETE, OPCODE_FEXISTS, OPCODE_MKDIR, OPCODE_FREADLINE, OPCODE_FWRITELINE, OPCODE_FLEN, OPCODE_PATHJOIN, OPCODE_PATHBASE, OPCODE_PATHDIR, OPCODE_PATHEXISTS, OPCODE_FLIST, OPCODE_HTTPGET, OPCODE_HTTPPOST, OPCODE_HTTPDOWN, OPCODE_JSONPARSE, OPCODE_JSONSTR, OPCODE_JSONGET, OPCODE_JSONSET, OPCODE_HTTPFILE, OPCODE_NETINFO, OPCODE_ZIP, OPCODE_UNZIP, OPCODE_SOCKCONN, OPCODE_SOCKSEND, OPCODE_SOCKRECV, OPCODE_SOCKCLOSE, OPCODE_OSNAME, OPCODE_OSARCH, OPCODE_OSLANG, OPCODE_OSHOST, OPCODE_SERVERBIND, OPCODE_SERVERLSTN, OPCODE_SERVERACCPT, OPCODE_SERVERSEND, OPCODE_SERVERRECV, OPCODE_SERVERCLS, OPCODE_DATE, OPCODE_DATEDMY, OPCODE_WEEKDAY, OPCODE_DAYOFYEAR, OPCODE_MONTH, OPCODE_YEAR, OPCODE_DAY, OPCODE_TIME, OPCODE_HOUR, OPCODE_MINUTE, OPCODE_ARGS, OPCODE_ARGGET, OPCODE_ARGLEN, OPCODE_SECOND, OPCODE_TIMESTAMP, OPCODE_SLEEP, OPCODE_FPS, OPCODE_TICK, OPCODE_SCHEDULE, OPCODE_TRY, OPCODE_CATCH, OPCODE_ENDTRY, OPCODE_THROW, OPCODE_ERRGET, OPCODE_PARAM, OPCODE_CALLP, OPCODE_FDIV, OPCODE_MIN, OPCODE_MAX, OPCODE_STRPAD, OPCODE_STRREPEAT, OPCODE_STRCOUNT, OPCODE_STRCMP, OPCODE_STRSLICE, OPCODE_SORT, OPCODE_REVERSE, OPCODE_SLICE, OPCODE_INDEXOF, OPCODE_UNIQUE, OPCODE_RANGE, OPCODE_FCOPY, OPCODE_FMOVE, OPCODE_FSTAT, OPCODE_FTOUCH, OPCODE_URLENCODE, OPCODE_URLDECODE, OPCODE_HTTPSTATUS, OPCODE_HTTPTIMEOUT, OPCODE_HTTPGETH, OPCODE_HTTPPOSTH, OPCODE_IMPORT, OPCODE_RANDINT, OPCODE_RANDSTR, OPCODE_RANDCHOICE, OPCODE_UUID, OPCODE_HASH, OPCODE_HASHSHA256, OPCODE_HASHMD5, OPCODE_ENCRYPT, OPCODE_DECRYPT, OPCODE_SHELLEXEC, OPCODE_EXIT
from bin.shared.math.MathModule import MathModule
from bin.shared.json.JsonModule import JsonModule
from bin.shared.fs.FsModule import FsModule
from bin.shared.os.OsModule import OsModule
from bin.shared.array.ArrayModule import ArrayModule
from bin.shared.data.DataModule import DataModule
from bin.shared.time.TimeModule import TimeModule
from bin.shared.schedule.ScheduleModule import ScheduleModule
from bin.shared.hash.HashModule import HashModule
from bin.shared.encrypt.EncryptModule import EncryptModule
from bin.shared.net.NetModule import NetModule
from bin.shared.random.RandomModule import RandomModule
from bin.shared.uuid.UuidModule import UuidModule
from bin.shared.string.StringModule import StringModule
from bin.shared.int.IntModule import IntModule
from bin.shared.zip.ZipModule import ZipModule
try:
    from fs.Sandbox import isProtectedManualPath
    from kernel.system.Constant import PROFILE_FILE
except Exception:
    isProtectedManualPath = None
    PROFILE_FILE = "profile.json"
class SharedInterpreter:
    def __init__(self, programName: str = None, isSudo: bool = False, vistroRoot: Path = None, username: str = None, role: str = None):
        self.isSudo = isSudo
        self.vars = {}
        self.functions = {}
        self.signals = {}
        self.callStack = []
        self.callFrames = []
        self.tryStack = []
        self.pendingThrow = None
        self.lastError = None
        self.httpTimeout = 10
        self.username = username
        self.role = role or "admin"
        self.args = []
        self.sockets = {}
        self.servers = {}
        self.output = []
        self.returnValue = None
        self.programName = programName
        if vistroRoot is not None:
            self.vistroRoot = vistroRoot
        else:
            try:
                from kernel.system.Constant import VISTRO_ROOT
                self.vistroRoot = VISTRO_ROOT
            except Exception:
                self.vistroRoot = Path.home() / "vistro" / "root"
    def getVar(self, name: str):
        return self.vars.get(name)
    def setVar(self, name: str, value):
        self.vars[name] = value
    def getLength(self, name: str) -> int:
        v = self.vars.get(name)
        if isinstance(v, list):
            return len(v)
        if isinstance(v, str):
            return len(v)
        return 0
    def getArgument(self, index: int):
        try:
            i = int(index or 0)
            return self.args[i] if 0 <= i < len(self.args) else None
        except Exception:
            return None
    def getImportBytecode(self, name: str):
        try:
            clean = str(name or "")
            if not clean or "/" in clean or "\\" in clean or ".." in clean:
                return None
            programPath = self.vistroRoot / "programs" / clean / "command.AppCommand"
            if programPath.exists():
                return self._fromHexFile(programPath.read_text(encoding="utf-8"))
        except Exception:
            pass
        return None
    def importModule(self, name: str) -> bool:
        importedBytecode = self.getImportBytecode(str(name or ""))
        if not importedBytecode:
            return False
        subInterp = SharedInterpreter(vistroRoot=self.vistroRoot, username=self.username, role=self.role)
        subInterp.functions = {}
        subInterp._scanFunctions(importedBytecode)
        for funcName, entry in subInterp.functions.items():
            start, end = entry if len(entry) == 2 else (entry[1], entry[2])
            self.functions[funcName] = (importedBytecode, start, end)
        return True
    def _scanTry(self, data: bytes, pos: int, end: int):
        errVar = None
        catchAfter = None
        depth = 1
        while pos < end:
            op = data[pos]
            pos += 1
            if op == OPCODE_TRY:
                depth += 1
            elif op == OPCODE_CATCH:
                if depth == 1 and catchAfter is None:
                    errVar, pos = self._readToken(data, pos)
                    catchAfter = pos
                    continue
                pos = self._skipInstruction(data, pos, op)
            elif op == OPCODE_ENDTRY:
                depth -= 1
                if depth == 0:
                    if catchAfter is None:
                        catchAfter = pos
                    return errVar, catchAfter, pos
            else:
                pos = self._skipInstruction(data, pos, op)
        if catchAfter is None:
            catchAfter = end
        return errVar, catchAfter, end
    def _skipToEndTry(self, data: bytes, pos: int, end: int) -> int:
        depth = 1
        while pos < end:
            op = data[pos]
            pos += 1
            if op == OPCODE_TRY:
                depth += 1
            elif op == OPCODE_ENDTRY:
                depth -= 1
                if depth == 0:
                    return pos
            else:
                pos = self._skipInstruction(data, pos, op)
        return end
    def _findMatchingEndif(self, data: bytes, pos: int, end: int) -> int:
        depth = 1
        while pos < end:
            op = data[pos]
            pos += 1
            if op == OPCODE_IF:
                pos = self._skipValue(data, pos)
                depth += 1
            elif op == OPCODE_ENDIF:
                depth -= 1
                if depth == 0:
                    return pos
            else:
                pos = self._skipInstruction(data, pos, op)
        return end
    def _findHandler(self, data: bytes, pos: int, end: int, throwPos: int):
        dataId = id(data)
        for i in range(len(self.tryStack) - 1, -1, -1):
            f = self.tryStack[i]
            if f["dataId"] == dataId and f["tryPos"] < throwPos < f["endAfter"] and pos <= f["catchAfter"] <= end:
                return i
        return None
    def _bindHandler(self, index: int, msg: str, conditionStack: list, loopStack: list):
        f = self.tryStack[index]
        del self.tryStack[index:]
        while len(conditionStack) > f["condDepth"]:
            conditionStack.pop()
        while len(loopStack) > f["loopDepth"]:
            loopStack.pop()
        if f["errVar"]:
            self.vars[f["errVar"]] = str(msg)
        self.lastError = str(msg)
        return f["catchAfter"]
    def _drainPending(self, data: bytes, pos: int, end: int, conditionStack: list, loopStack: list):
        if self.pendingThrow is None:
            return pos
        tpos, tmsg, tid = self.pendingThrow
        self.pendingThrow = None
        if tid != id(data):
            self.pendingThrow = (tpos, tmsg, tid)
            return end
        idx = self._findHandler(data, pos, end, tpos)
        if idx is None:
            self.pendingThrow = (tpos, tmsg, tid)
            return end
        return self._bindHandler(idx, tmsg, conditionStack, loopStack)
    def handleExtension(self, opcode: int, data: bytes, pos: int, end: int, executing: bool):
        return None
    def skipExtension(self, opcode: int, data: bytes, pos: int):
        return None
    def _sandboxPath(self, path: str) -> Path:
        p = Path(path)
        if not p.is_absolute():
            if self.programName:
                base = self.vistroRoot / "programs" / self.programName
            else:
                base = self.vistroRoot
            p = base / p
        resolved = p.resolve()
        try:
            resolved.relative_to(self.vistroRoot.resolve())
        except ValueError:
            raise PermissionError(f"Access denied: {path}")
        if self.programName:
            try:
                resolved.relative_to((self.vistroRoot / "programs" / self.programName).resolve())
            except ValueError:
                try:
                    resolved.relative_to((self.vistroRoot / "data" / self.programName).resolve())
                except ValueError:
                    raise PermissionError(f"Program can only access its own directory: {path}")
        elif self.role != "admin":
            try:
                resolved.relative_to((self.vistroRoot / "users" / str(self.username or "")).resolve())
            except ValueError:
                raise PermissionError(f"Access denied: {path}")
        return resolved
    def _readUShort(self, data: bytes, pos: int):
        val = struct.unpack(">H", data[pos:pos+2])[0]
        return val, pos+2
    def _readLong(self, data: bytes, pos: int):
        val = struct.unpack(">q", data[pos:pos+8])[0]
        return val, pos+8
    def _readBool(self, data: bytes, pos: int):
        val = data[pos]
        return bool(val), pos+1
    def _readToken(self, data: bytes, pos: int):
        length, pos = self._readUShort(data, pos)
        token = data[pos:pos+length].decode("utf-8")
        return token, pos+length
    def _readStr(self, data: bytes, pos: int):
        length, pos = self._readUShort(data, pos)
        s = data[pos:pos+length].decode("utf-8")
        return s, pos+length
    def _readValue(self, data: bytes, pos: int):
        typeTag = data[pos]
        pos += 1
        if typeTag == 0x01:
            val, pos = self._readStr(data, pos)
            return val, pos
        elif typeTag == 0x02:
            val, pos = self._readLong(data, pos)
            return val, pos
        elif typeTag == 0x03:
            val, pos = self._readBool(data, pos)
            return val, pos
        elif typeTag == 0x04:
            ref, pos = self._readToken(data, pos)
            return self.vars.get(ref, None), pos
        elif typeTag == 0x00:
            return None, pos
        return None, pos
    def _readValueMeta(self, data: bytes, pos: int):
        typeTag = data[pos]
        pos += 1
        if typeTag == 0x01:
            val, pos = self._readStr(data, pos)
            return val, False, None, pos
        elif typeTag == 0x02:
            val, pos = self._readLong(data, pos)
            return val, False, None, pos
        elif typeTag == 0x03:
            val, pos = self._readBool(data, pos)
            return val, False, None, pos
        elif typeTag == 0x04:
            ref, pos = self._readToken(data, pos)
            return self.vars.get(ref, None), True, ref, pos
        elif typeTag == 0x00:
            return None, False, None, pos
        return None, False, None, pos
    def _evalCondition(self, val) -> bool:
        if isinstance(val, bool):
            return val
        if isinstance(val, int):
            return val != 0
        if isinstance(val, str):
            return val.lower() not in ("false", "0", "")
        return bool(val)
    def _print(self, val, newline: bool = True):
        s = str(val) if val is not None else ""
        self.output.append(s + ("\n" if newline else ""))
    def execute(self, bytecode: bytes, args: list = None) -> str:
        self.args = args or []
        self.vars = {"SUDO": self.isSudo}
        self.functions = {}
        self.signals = {}
        self.callStack = []
        self.callFrames = []
        self.tryStack = []
        self.pendingThrow = None
        self.lastError = None
        self.output = []
        self.returnValue = None
        self._scanFunctions(bytecode)
        pos = 0
        pos = self._executeBlock(bytecode, pos, len(bytecode))
        if self.pendingThrow is not None:
            _, tmsg, _ = self.pendingThrow
            self.pendingThrow = None
            self._print(f"[ERR] Uncaught: {tmsg}")
        return "".join(self.output)
    def _scanFunctions(self, data: bytes):
        pos = 0
        while pos < len(data):
            if pos >= len(data):
                break
            opcode = data[pos]
            pos += 1
            if opcode == OPCODE_FUNC:
                name, pos = self._readToken(data, pos)
                start = pos
                depth = 1
                while pos < len(data) and depth > 0:
                    op = data[pos]
                    pos += 1
                    if op == OPCODE_FUNC:
                        _, pos = self._readToken(data, pos)
                        depth += 1
                    elif op == OPCODE_ENDFUNC:
                        depth -= 1
                    else:
                        pos = self._skipInstruction(data, pos, op)
                self.functions[name] = (data, start, pos - 1)
            else:
                pos = self._skipInstruction(data, pos, opcode)
    def _skipValue(self, data: bytes, pos: int) -> int:
        try:
            typeTag = data[pos]
            pos += 1
            if typeTag == 0x00:
                pass
            elif typeTag == 0x01:
                l, pos = self._readUShort(data, pos)
                pos += l
            elif typeTag == 0x02:
                pos += 8
            elif typeTag == 0x03:
                pos += 1
            elif typeTag == 0x04:
                _, pos = self._readToken(data, pos)
        except Exception:
            pass
        return pos
    def _skipInstruction(self, data: bytes, pos: int, opcode: int) -> int:
        try:
            if opcode in (OPCODE_ELSE, OPCODE_ENDIF, OPCODE_ENDWHILE, OPCODE_BREAK, OPCODE_CONTINUE, OPCODE_ENDFUNC, OPCODE_EXIT, OPCODE_TRY, OPCODE_ENDTRY):
                pass
            elif opcode == OPCODE_FUNC:
                _, pos = self._readToken(data, pos)
            elif opcode in (OPCODE_ARGS, OPCODE_ARGLEN, OPCODE_OSNAME, OPCODE_OSARCH, OPCODE_OSLANG, OPCODE_OSHOST, OPCODE_DATE, OPCODE_DATEDMY, OPCODE_WEEKDAY, OPCODE_DAYOFYEAR, OPCODE_MONTH, OPCODE_YEAR, OPCODE_DAY, OPCODE_TIME, OPCODE_HOUR, OPCODE_MINUTE, OPCODE_SECOND, OPCODE_TIMESTAMP, OPCODE_FPS, OPCODE_TICK, OPCODE_UUID, OPCODE_NETINFO, OPCODE_CATCH, OPCODE_ERRGET, OPCODE_PARAM, 0xF4):
                _, pos = self._readToken(data, pos)
            elif opcode == OPCODE_LIST:
                _, pos = self._readToken(data, pos)
                count = data[pos]
                pos += 1
                for _ in range(count):
                    pos = self._skipValue(data, pos)
            elif opcode in (OPCODE_FWRITE, OPCODE_FAPPEND, OPCODE_SOCKSEND, OPCODE_SERVERSEND, OPCODE_ZIP, OPCODE_UNZIP, OPCODE_FCOPY, OPCODE_FMOVE):
                pos = self._skipValue(data, pos)
                pos = self._skipValue(data, pos)
            elif opcode == OPCODE_CALLP:
                _, pos = self._readToken(data, pos)
                pos = self._skipValue(data, pos)
                count = data[pos]
                pos += 1
                for _ in range(count):
                    pos = self._skipValue(data, pos)
            elif opcode == OPCODE_FWRITELINE:
                pos = self._skipValue(data, pos)
                pos = self._skipValue(data, pos)
                pos = self._skipValue(data, pos)
            elif opcode in (OPCODE_SUBSTR, OPCODE_STRREPLACE, OPCODE_JSONSET, OPCODE_INTCLAMP, OPCODE_STRPAD, OPCODE_STRSLICE, OPCODE_SLICE):
                _, pos = self._readToken(data, pos)
                pos = self._skipValue(data, pos)
                pos = self._skipValue(data, pos)
                pos = self._skipValue(data, pos)
            elif opcode in (OPCODE_ADD, OPCODE_SUB, OPCODE_MUL, OPCODE_DIV, OPCODE_MOD, OPCODE_EQ, OPCODE_NEQ, OPCODE_LT, OPCODE_GT, OPCODE_LTE, OPCODE_GTE, OPCODE_AND, OPCODE_OR, OPCODE_CONCAT, OPCODE_POW, OPCODE_STRFIND, OPCODE_STRSTARTS, OPCODE_STRENDS, OPCODE_STRCHAR, OPCODE_STRJOIN, OPCODE_LISTGET, OPCODE_LISTSET, OPCODE_LISTCONTAINS, OPCODE_LISTJOIN, OPCODE_JSONGET, OPCODE_PATHJOIN, OPCODE_ENCRYPT, OPCODE_DECRYPT, OPCODE_RANDINT, OPCODE_RANDSTR, OPCODE_HTTPPOST, OPCODE_SOCKCONN, OPCODE_FREADLINE, OPCODE_FDIV, OPCODE_MIN, OPCODE_MAX, OPCODE_STRREPEAT, OPCODE_STRCOUNT, OPCODE_STRCMP, OPCODE_INDEXOF, OPCODE_RANGE, OPCODE_HTTPGETH, OPCODE_HTTPPOSTH):
                _, pos = self._readToken(data, pos)
                pos = self._skipValue(data, pos)
                pos = self._skipValue(data, pos)
            elif opcode in (OPCODE_PRINT, OPCODE_PRINTLN, OPCODE_IF, OPCODE_ELIF, OPCODE_WHILE, OPCODE_CALL, OPCODE_RETURN, OPCODE_IMPORT, OPCODE_SIGNAL, OPCODE_EMIT, OPCODE_SLEEP, OPCODE_FDELETE, OPCODE_MKDIR, OPCODE_SERVERLSTN, OPCODE_THROW, OPCODE_HTTPTIMEOUT, OPCODE_FTOUCH, 0xF1, 0xF2, 0xF3):
                pos = self._skipValue(data, pos)
            else:
                skipped = self.skipExtension(opcode, data, pos)
                if skipped is not None:
                    pos = skipped
                else:
                    _, pos = self._readToken(data, pos)
                    pos = self._skipValue(data, pos)
        except Exception:
            pass
        return pos
    def _findMatchingEndWhile(self, data: bytes, pos: int, end: int) -> int:
        depth = 1
        while pos < end:
            op = data[pos]
            pos += 1
            if op == OPCODE_WHILE:
                pos = self._skipValue(data, pos)
                depth += 1
            elif op == OPCODE_ENDWHILE:
                depth -= 1
                if depth == 0:
                    return pos
            else:
                pos = self._skipInstruction(data, pos, op)
        return end
    def _executeBlock(self, data: bytes, pos: int, end: int) -> int:
        conditionStack = []
        loopStack = []
        executing = True
        while pos < end:
            opcode = data[pos]
            pos += 1
            if opcode == OPCODE_VAR_STR:
                name, pos = self._readToken(data, pos)
                val, pos = self._readValue(data, pos)
                if executing:
                    self.vars[name] = str(val) if val is not None else ""
            elif opcode == OPCODE_VAR_INT:
                name, pos = self._readToken(data, pos)
                val, pos = self._readValue(data, pos)
                if executing:
                    try:
                        self.vars[name] = int(val) if val is not None else 0
                    except Exception:
                        self.vars[name] = 0
            elif opcode == OPCODE_VAR_BOOL:
                name, pos = self._readToken(data, pos)
                val, pos = self._readValue(data, pos)
                if executing:
                    self.vars[name] = bool(val) if val is not None else False
            elif opcode == OPCODE_SET:
                name, pos = self._readToken(data, pos)
                val, pos = self._readValue(data, pos)
                if executing:
                    self.vars[name] = val
            elif opcode == OPCODE_PRINT:
                val, pos = self._readValue(data, pos)
                if executing:
                    self._print(val, newline=False)
            elif opcode == OPCODE_PRINTLN:
                val, pos = self._readValue(data, pos)
                if executing:
                    self._print(val, newline=True)
            elif opcode == OPCODE_IF:
                val, pos = self._readValue(data, pos)
                cond = self._evalCondition(val)
                conditionStack.append(("if", cond, executing))
                if not executing:
                    executing = False
                else:
                    executing = cond
            elif opcode == OPCODE_ELIF:
                val, pos = self._readValue(data, pos)
                if conditionStack:
                    frame = conditionStack[-1]
                    parentExec = frame[2]
                    if frame[1] or not parentExec:
                        executing = False
                    else:
                        cond = self._evalCondition(val)
                        executing = cond
                        conditionStack[-1] = ("elif", cond, parentExec)
            elif opcode == OPCODE_ELSE:
                if conditionStack:
                    frame = conditionStack[-1]
                    parentExec = frame[2]
                    if frame[1]:
                        executing = False
                    else:
                        executing = parentExec
            elif opcode == OPCODE_ENDIF:
                if conditionStack:
                    _, _, parentExec = conditionStack.pop()
                    executing = parentExec
            elif opcode == OPCODE_WHILE:
                val, isRef, refName, pos = self._readValueMeta(data, pos)
                if not executing:
                    pos = self._findMatchingEndWhile(data, pos, end)
                else:
                    cond = self._evalCondition(val)
                    if cond:
                        loopStack.append({"start": pos, "ref": refName if isRef else None, "val": val if not isRef else None})
                    else:
                        pos = self._findMatchingEndWhile(data, pos, end)
            elif opcode == OPCODE_ENDWHILE:
                if not executing:
                    pass
                elif not loopStack:
                    pass
                else:
                    top = loopStack[-1]
                    if top["ref"] is not None:
                        cur = self.vars.get(top["ref"], None)
                        cond = self._evalCondition(cur)
                    else:
                        cond = self._evalCondition(top["val"])
                    if cond:
                        pos = top["start"]
                    else:
                        loopStack.pop()
            elif opcode == OPCODE_BREAK:
                if executing and loopStack:
                    loopStack.pop()
                    pos = self._findMatchingEndWhile(data, pos, end)
            elif opcode == OPCODE_CONTINUE:
                if executing and loopStack:
                    top = loopStack[-1]
                    if top["ref"] is not None:
                        cur = self.vars.get(top["ref"], None)
                        cond = self._evalCondition(cur)
                    else:
                        cond = self._evalCondition(top["val"])
                    if cond:
                        pos = top["start"]
                    else:
                        loopStack.pop()
            elif opcode == OPCODE_SIGNAL:
                nameVal, pos = self._readValue(data, pos)
                if executing and nameVal is not None:
                    self.signals[str(nameVal)] = True
            elif opcode == OPCODE_TRY:
                tryOpcodePos = pos - 1
                if executing:
                    errVar, catchAfter, endAfter = self._scanTry(data, pos, end)
                    self.tryStack.append({"dataId": id(data), "tryPos": tryOpcodePos, "catchAfter": catchAfter, "endAfter": endAfter, "errVar": errVar, "condDepth": len(conditionStack), "loopDepth": len(loopStack)})
                else:
                    pos = self._skipToEndTry(data, pos, end)
            elif opcode == OPCODE_CATCH:
                dest, pos = self._readToken(data, pos)
                if executing:
                    if self.tryStack and self.tryStack[-1]["dataId"] == id(data) and self.tryStack[-1]["catchAfter"] == pos:
                        self.tryStack.pop()
                    pos = self._skipToEndTry(data, pos, end)
            elif opcode == OPCODE_ENDTRY:
                if executing and self.tryStack and self.tryStack[-1]["dataId"] == id(data) and self.tryStack[-1]["endAfter"] == pos:
                    self.tryStack.pop()
            elif opcode == OPCODE_THROW:
                val, pos = self._readValue(data, pos)
                if executing:
                    msg = str(val) if val is not None else ""
                    idx = self._findHandler(data, pos, end, pos)
                    if idx is None:
                        self.pendingThrow = (pos, msg, id(data))
                        return end
                    pos = self._bindHandler(idx, msg, conditionStack, loopStack)
            elif opcode == OPCODE_ERRGET:
                dest, pos = self._readToken(data, pos)
                if executing:
                    self.vars[dest] = self.lastError
            elif opcode == OPCODE_PARAM:
                dest, pos = self._readToken(data, pos)
                if executing:
                    if self.callFrames:
                        frame = self.callFrames[-1]
                        items = frame["args"]
                        at = frame["index"]
                        self.vars[dest] = items[at] if 0 <= at < len(items) else None
                        frame["index"] = at + 1
                    else:
                        self.vars[dest] = None
            elif opcode == OPCODE_CALLP:
                dest, pos = self._readToken(data, pos)
                funcVal, pos = self._readValue(data, pos)
                count = data[pos]
                pos += 1
                callArgs = []
                for _ in range(count):
                    v, pos = self._readValue(data, pos)
                    callArgs.append(v)
                if executing and funcVal is not None:
                    funcName = str(funcVal)
                    if funcName in self.functions:
                        entry = self.functions[funcName]
                        fcode, start, fend = entry if len(entry) == 3 else (data, entry[0], entry[1])
                        savedVars = dict(self.vars)
                        self.callFrames.append({"args": list(callArgs), "index": 0})
                        self._executeBlock(fcode, start, fend)
                        if self.callFrames:
                            self.callFrames.pop()
                        ret = self.returnValue
                        self.vars = savedVars
                        self.returnValue = None
                        self.vars[dest] = ret
                        pos = self._drainPending(data, pos, end, conditionStack, loopStack)
            elif opcode == OPCODE_EMIT:
                nameVal, pos = self._readValue(data, pos)
                if executing and nameVal is not None:
                    funcName = str(nameVal)
                    if funcName in self.functions:
                        entry = self.functions[funcName]
                        fcode, start, fend = entry if len(entry) == 3 else (data, entry[0], entry[1])
                        savedVars = dict(self.vars)
                        self._executeBlock(fcode, start, fend)
                        ret = self.returnValue
                        self.vars = savedVars
                        self.returnValue = None
                        pos = self._drainPending(data, pos, end, conditionStack, loopStack)
            elif opcode == OPCODE_FUNC:
                name, pos = self._readToken(data, pos)
                depth = 1
                while pos < end and depth > 0:
                    op = data[pos]
                    pos += 1
                    if op == OPCODE_FUNC:
                        _, pos = self._readToken(data, pos)
                        depth += 1
                    elif op == OPCODE_ENDFUNC:
                        depth -= 1
                    else:
                        pos = self._skipInstruction(data, pos, op)
            elif opcode == OPCODE_ENDFUNC:
                break
            elif opcode == OPCODE_CALL:
                nameVal, pos = self._readValue(data, pos)
                if executing and nameVal is not None:
                    funcName = str(nameVal)
                    if funcName in self.functions:
                        entry = self.functions[funcName]
                        fcode, start, fend = entry if len(entry) == 3 else (data, entry[0], entry[1])
                        savedVars = dict(self.vars)
                        self._executeBlock(fcode, start, fend)
                        ret = self.returnValue
                        self.vars = savedVars
                        self.returnValue = None
                        pos = self._drainPending(data, pos, end, conditionStack, loopStack)
            elif opcode == OPCODE_RETURN:
                val, pos = self._readValue(data, pos)
                if executing:
                    self.returnValue = val
                    return pos
            elif opcode == OPCODE_ADD:
                dest, pos = self._readToken(data, pos)
                a, pos = self._readValue(data, pos)
                b, pos = self._readValue(data, pos)
                if executing:
                    try:
                        self.vars[dest] = (a or 0) + (b or 0)
                    except Exception:
                        self.vars[dest] = 0
            elif opcode == OPCODE_SUB:
                dest, pos = self._readToken(data, pos)
                a, pos = self._readValue(data, pos)
                b, pos = self._readValue(data, pos)
                if executing:
                    try:
                        self.vars[dest] = (a or 0) - (b or 0)
                    except Exception:
                        self.vars[dest] = 0
            elif opcode == OPCODE_MUL:
                dest, pos = self._readToken(data, pos)
                a, pos = self._readValue(data, pos)
                b, pos = self._readValue(data, pos)
                if executing:
                    try:
                        self.vars[dest] = (a or 0) * (b or 0)
                    except Exception:
                        self.vars[dest] = 0
            elif opcode == OPCODE_DIV:
                dest, pos = self._readToken(data, pos)
                a, pos = self._readValue(data, pos)
                b, pos = self._readValue(data, pos)
                if executing:
                    bv = b or 0
                    try:
                        self.vars[dest] = (a or 0) // bv if bv != 0 else 0
                    except Exception:
                        self.vars[dest] = 0
            elif opcode == OPCODE_MOD:
                dest, pos = self._readToken(data, pos)
                a, pos = self._readValue(data, pos)
                b, pos = self._readValue(data, pos)
                if executing:
                    bv = b or 0
                    try:
                        self.vars[dest] = (a or 0) % bv if bv != 0 else 0
                    except Exception:
                        self.vars[dest] = 0
            elif opcode == OPCODE_ROUND:
                dest, pos = self._readToken(data, pos)
                v, pos = self._readValue(data, pos)
                if executing:
                    self.vars[dest] = MathModule.roundValue(v)
            elif opcode == OPCODE_FLOOR:
                dest, pos = self._readToken(data, pos)
                v, pos = self._readValue(data, pos)
                if executing:
                    self.vars[dest] = MathModule.floorValue(v)
            elif opcode == OPCODE_CEIL:
                dest, pos = self._readToken(data, pos)
                v, pos = self._readValue(data, pos)
                if executing:
                    self.vars[dest] = MathModule.ceilValue(v)
            elif opcode == OPCODE_SQRT:
                dest, pos = self._readToken(data, pos)
                v, pos = self._readValue(data, pos)
                if executing:
                    self.vars[dest] = MathModule.sqrtValue(v)
            elif opcode == OPCODE_POW:
                dest, pos = self._readToken(data, pos)
                a, pos = self._readValue(data, pos)
                b, pos = self._readValue(data, pos)
                if executing:
                    self.vars[dest] = MathModule.powValue(a, b)
            elif opcode == OPCODE_ABS:
                dest, pos = self._readToken(data, pos)
                v, pos = self._readValue(data, pos)
                if executing:
                    self.vars[dest] = MathModule.absValue(v)
            elif opcode == OPCODE_ISODD:
                dest, pos = self._readToken(data, pos)
                v, pos = self._readValue(data, pos)
                if executing:
                    self.vars[dest] = MathModule.isOdd(v)
            elif opcode == OPCODE_ISEVEN:
                dest, pos = self._readToken(data, pos)
                v, pos = self._readValue(data, pos)
                if executing:
                    self.vars[dest] = MathModule.isEven(v)
            elif opcode == OPCODE_FDIV:
                dest, pos = self._readToken(data, pos)
                a, pos = self._readValue(data, pos)
                b, pos = self._readValue(data, pos)
                if executing:
                    self.vars[dest] = MathModule.fdivValue(a, b)
            elif opcode == OPCODE_MIN:
                dest, pos = self._readToken(data, pos)
                a, pos = self._readValue(data, pos)
                b, pos = self._readValue(data, pos)
                if executing:
                    self.vars[dest] = MathModule.minValue(a, b)
            elif opcode == OPCODE_MAX:
                dest, pos = self._readToken(data, pos)
                a, pos = self._readValue(data, pos)
                b, pos = self._readValue(data, pos)
                if executing:
                    self.vars[dest] = MathModule.maxValue(a, b)
            elif opcode == OPCODE_ISINT:
                dest, pos = self._readToken(data, pos)
                v, pos = self._readValue(data, pos)
                if executing:
                    self.vars[dest] = IntModule.isInteger(v)
            elif opcode == OPCODE_INTPARSE:
                dest, pos = self._readToken(data, pos)
                v, pos = self._readValue(data, pos)
                if executing:
                    self.vars[dest] = IntModule.parseInt(v)
            elif opcode == OPCODE_INTSTR:
                dest, pos = self._readToken(data, pos)
                v, pos = self._readValue(data, pos)
                if executing:
                    self.vars[dest] = IntModule.toString(v)
            elif opcode == OPCODE_INTCLAMP:
                dest, pos = self._readToken(data, pos)
                v, pos = self._readValue(data, pos)
                lo, pos = self._readValue(data, pos)
                hi, pos = self._readValue(data, pos)
                if executing:
                    self.vars[dest] = IntModule.clampValue(v, lo, hi)
            elif opcode == OPCODE_EQ:
                dest, pos = self._readToken(data, pos)
                a, pos = self._readValue(data, pos)
                b, pos = self._readValue(data, pos)
                if executing:
                    self.vars[dest] = a == b
            elif opcode == OPCODE_NEQ:
                dest, pos = self._readToken(data, pos)
                a, pos = self._readValue(data, pos)
                b, pos = self._readValue(data, pos)
                if executing:
                    self.vars[dest] = a != b
            elif opcode == OPCODE_LT:
                dest, pos = self._readToken(data, pos)
                a, pos = self._readValue(data, pos)
                b, pos = self._readValue(data, pos)
                if executing:
                    try:
                        self.vars[dest] = (a or 0) < (b or 0)
                    except Exception:
                        self.vars[dest] = False
            elif opcode == OPCODE_GT:
                dest, pos = self._readToken(data, pos)
                a, pos = self._readValue(data, pos)
                b, pos = self._readValue(data, pos)
                if executing:
                    try:
                        self.vars[dest] = (a or 0) > (b or 0)
                    except Exception:
                        self.vars[dest] = False
            elif opcode == OPCODE_LTE:
                dest, pos = self._readToken(data, pos)
                a, pos = self._readValue(data, pos)
                b, pos = self._readValue(data, pos)
                if executing:
                    try:
                        self.vars[dest] = (a or 0) <= (b or 0)
                    except Exception:
                        self.vars[dest] = False
            elif opcode == OPCODE_GTE:
                dest, pos = self._readToken(data, pos)
                a, pos = self._readValue(data, pos)
                b, pos = self._readValue(data, pos)
                if executing:
                    try:
                        self.vars[dest] = (a or 0) >= (b or 0)
                    except Exception:
                        self.vars[dest] = False
            elif opcode == OPCODE_AND:
                dest, pos = self._readToken(data, pos)
                a, pos = self._readValue(data, pos)
                b, pos = self._readValue(data, pos)
                if executing:
                    self.vars[dest] = bool(a) and bool(b)
            elif opcode == OPCODE_OR:
                dest, pos = self._readToken(data, pos)
                a, pos = self._readValue(data, pos)
                b, pos = self._readValue(data, pos)
                if executing:
                    self.vars[dest] = bool(a) or bool(b)
            elif opcode == OPCODE_NOT:
                dest, pos = self._readToken(data, pos)
                val, pos = self._readValue(data, pos)
                if executing:
                    self.vars[dest] = not bool(val)
            elif opcode == OPCODE_CONCAT:
                dest, pos = self._readToken(data, pos)
                a, pos = self._readValue(data, pos)
                b, pos = self._readValue(data, pos)
                if executing:
                    self.vars[dest] = str(a or "") + str(b or "")
            elif opcode == OPCODE_STRLEN:
                dest, pos = self._readToken(data, pos)
                val, pos = self._readValue(data, pos)
                if executing:
                    self.vars[dest] = len(str(val or ""))
            elif opcode == OPCODE_SUBSTR:
                dest, pos = self._readToken(data, pos)
                s, pos = self._readValue(data, pos)
                start, pos = self._readValue(data, pos)
                length, pos = self._readValue(data, pos)
                if executing:
                    sv = str(s or "")
                    st = int(start or 0)
                    ln = int(length or 0)
                    self.vars[dest] = sv[st:st+ln]
            elif opcode == OPCODE_UPPER:
                dest, pos = self._readToken(data, pos)
                val, pos = self._readValue(data, pos)
                if executing:
                    self.vars[dest] = str(val or "").upper()
            elif opcode == OPCODE_LOWER:
                dest, pos = self._readToken(data, pos)
                val, pos = self._readValue(data, pos)
                if executing:
                    self.vars[dest] = str(val or "").lower()
            elif opcode == OPCODE_SPLIT:
                dest, pos = self._readToken(data, pos)
                s, pos = self._readValue(data, pos)
                sep, pos = self._readValue(data, pos)
                if executing:
                    self.vars[dest] = str(s or "").split(str(sep or " "))
            elif opcode == OPCODE_STRIS:
                dest, pos = self._readToken(data, pos)
                v, pos = self._readValue(data, pos)
                if executing:
                    self.vars[dest] = StringModule.isString(v)
            elif opcode == OPCODE_STRFIND:
                dest, pos = self._readToken(data, pos)
                h, pos = self._readValue(data, pos)
                n, pos = self._readValue(data, pos)
                if executing:
                    self.vars[dest] = StringModule.findText(h, n)
            elif opcode == OPCODE_STRREPLACE:
                dest, pos = self._readToken(data, pos)
                s, pos = self._readValue(data, pos)
                old, pos = self._readValue(data, pos)
                new, pos = self._readValue(data, pos)
                if executing:
                    self.vars[dest] = StringModule.replaceText(s, old, new)
            elif opcode == OPCODE_STRTRIM:
                dest, pos = self._readToken(data, pos)
                v, pos = self._readValue(data, pos)
                if executing:
                    self.vars[dest] = StringModule.trimText(v)
            elif opcode == OPCODE_STRSTARTS:
                dest, pos = self._readToken(data, pos)
                s, pos = self._readValue(data, pos)
                p, pos = self._readValue(data, pos)
                if executing:
                    self.vars[dest] = StringModule.startsWith(s, p)
            elif opcode == OPCODE_STRENDS:
                dest, pos = self._readToken(data, pos)
                s, pos = self._readValue(data, pos)
                p, pos = self._readValue(data, pos)
                if executing:
                    self.vars[dest] = StringModule.endsWith(s, p)
            elif opcode == OPCODE_STRREV:
                dest, pos = self._readToken(data, pos)
                v, pos = self._readValue(data, pos)
                if executing:
                    self.vars[dest] = StringModule.reverseText(v)
            elif opcode == OPCODE_STRJOIN:
                dest, pos = self._readToken(data, pos)
                l, pos = self._readValue(data, pos)
                sep, pos = self._readValue(data, pos)
                if executing:
                    self.vars[dest] = StringModule.joinTexts(l, sep)
            elif opcode == OPCODE_STRCHAR:
                dest, pos = self._readToken(data, pos)
                s, pos = self._readValue(data, pos)
                idx, pos = self._readValue(data, pos)
                if executing:
                    self.vars[dest] = StringModule.charAt(s, idx)
            elif opcode == OPCODE_STRPAD:
                dest, pos = self._readToken(data, pos)
                s, pos = self._readValue(data, pos)
                width, pos = self._readValue(data, pos)
                pad, pos = self._readValue(data, pos)
                if executing:
                    self.vars[dest] = StringModule.padText(s, width, pad)
            elif opcode == OPCODE_STRREPEAT:
                dest, pos = self._readToken(data, pos)
                s, pos = self._readValue(data, pos)
                count, pos = self._readValue(data, pos)
                if executing:
                    self.vars[dest] = StringModule.repeatText(s, count)
            elif opcode == OPCODE_STRCOUNT:
                dest, pos = self._readToken(data, pos)
                h, pos = self._readValue(data, pos)
                n, pos = self._readValue(data, pos)
                if executing:
                    self.vars[dest] = StringModule.countText(h, n)
            elif opcode == OPCODE_STRCMP:
                dest, pos = self._readToken(data, pos)
                a, pos = self._readValue(data, pos)
                b, pos = self._readValue(data, pos)
                if executing:
                    self.vars[dest] = StringModule.cmpText(a, b)
            elif opcode == OPCODE_STRSLICE:
                dest, pos = self._readToken(data, pos)
                s, pos = self._readValue(data, pos)
                start, pos = self._readValue(data, pos)
                stop, pos = self._readValue(data, pos)
                if executing:
                    self.vars[dest] = StringModule.sliceText(s, start, stop)
            elif opcode == OPCODE_LIST:
                dest, pos = self._readToken(data, pos)
                count = data[pos]
                pos += 1
                items = []
                for _ in range(count):
                    v, pos = self._readValue(data, pos)
                    items.append(v)
                if executing:
                    self.vars[dest] = items
            elif opcode == OPCODE_ARRCREATE:
                dest, pos = self._readToken(data, pos)
                count = data[pos]
                pos += 1
                items = []
                for _ in range(count):
                    v, pos = self._readValue(data, pos)
                    items.append(v)
                if executing:
                    self.vars[dest] = ArrayModule.createArray(items)
            elif opcode == OPCODE_LISTGET:
                dest, pos = self._readToken(data, pos)
                lst, pos = self._readValue(data, pos)
                idx, pos = self._readValue(data, pos)
                if executing:
                    self.vars[dest] = ArrayModule.getItem(lst, idx)
            elif opcode == OPCODE_LISTLEN:
                dest, pos = self._readToken(data, pos)
                lst, pos = self._readValue(data, pos)
                if executing:
                    l = lst if isinstance(lst, list) else []
                    self.vars[dest] = len(l)
            elif opcode == OPCODE_LISTAPPEND:
                dest, pos = self._readToken(data, pos)
                val, pos = self._readValue(data, pos)
                if executing:
                    if dest not in self.vars or not isinstance(self.vars[dest], list):
                        self.vars[dest] = []
                    self.vars[dest].append(val)
            elif opcode == OPCODE_LISTSET:
                dest, pos = self._readToken(data, pos)
                idx, pos = self._readValue(data, pos)
                val, pos = self._readValue(data, pos)
                if executing:
                    cur = self.vars.get(dest, [])
                    self.vars[dest] = ArrayModule.setItem(cur, idx, val)
            elif opcode == OPCODE_LISTREMOVE:
                dest, pos = self._readToken(data, pos)
                idx, pos = self._readValue(data, pos)
                if executing:
                    cur = self.vars.get(dest, [])
                    self.vars[dest] = ArrayModule.removeItem(cur, idx)
            elif opcode == OPCODE_LISTCONTAINS:
                dest, pos = self._readToken(data, pos)
                lst, pos = self._readValue(data, pos)
                needle, pos = self._readValue(data, pos)
                if executing:
                    self.vars[dest] = ArrayModule.containsValue(lst, needle)
            elif opcode == OPCODE_LISTJOIN:
                dest, pos = self._readToken(data, pos)
                lst, pos = self._readValue(data, pos)
                sep, pos = self._readValue(data, pos)
                if executing:
                    self.vars[dest] = ArrayModule.joinValues(lst, sep)
            elif opcode == OPCODE_SORT:
                dest, pos = self._readToken(data, pos)
                lst, pos = self._readValue(data, pos)
                if executing:
                    cur = self.vars.get(dest, lst)
                    self.vars[dest] = ArrayModule.sortValues(cur if isinstance(cur, list) else lst)
            elif opcode == OPCODE_REVERSE:
                dest, pos = self._readToken(data, pos)
                lst, pos = self._readValue(data, pos)
                if executing:
                    cur = self.vars.get(dest, lst)
                    self.vars[dest] = ArrayModule.reverseValues(cur if isinstance(cur, list) else lst)
            elif opcode == OPCODE_SLICE:
                dest, pos = self._readToken(data, pos)
                lst, pos = self._readValue(data, pos)
                start, pos = self._readValue(data, pos)
                stop, pos = self._readValue(data, pos)
                if executing:
                    self.vars[dest] = ArrayModule.sliceValues(lst, start, stop)
            elif opcode == OPCODE_INDEXOF:
                dest, pos = self._readToken(data, pos)
                lst, pos = self._readValue(data, pos)
                needle, pos = self._readValue(data, pos)
                if executing:
                    self.vars[dest] = ArrayModule.indexOf(lst, needle)
            elif opcode == OPCODE_UNIQUE:
                dest, pos = self._readToken(data, pos)
                lst, pos = self._readValue(data, pos)
                if executing:
                    cur = self.vars.get(dest, lst)
                    self.vars[dest] = ArrayModule.uniqueValues(cur if isinstance(cur, list) else lst)
            elif opcode == OPCODE_RANGE:
                dest, pos = self._readToken(data, pos)
                start, pos = self._readValue(data, pos)
                stop, pos = self._readValue(data, pos)
                if executing:
                    self.vars[dest] = ArrayModule.rangeValues(start, stop)
            elif opcode == OPCODE_FOPEN:
                dest, pos = self._readToken(data, pos)
                path, pos = self._readValue(data, pos)
                if executing:
                    try:
                        p = self._sandboxPath(str(path or ""))
                        self.vars[dest] = str(p)
                    except PermissionError as e:
                        idx = self._findHandler(data, pos, end, pos)
                        if idx is None:
                            self.vars[dest] = None
                            self._print(f"[ERR] {e}")
                        else:
                            pos = self._bindHandler(idx, str(e), conditionStack, loopStack)
            elif opcode == OPCODE_FREAD:
                dest, pos = self._readToken(data, pos)
                path, pos = self._readValue(data, pos)
                if executing:
                    try:
                        p = self._sandboxPath(str(path or ""))
                        self.vars[dest] = p.read_text(encoding="utf-8") if p.exists() else None
                    except PermissionError as e:
                        idx = self._findHandler(data, pos, end, pos)
                        if idx is None:
                            self.vars[dest] = None
                            self._print(f"[ERR] {e}")
                        else:
                            pos = self._bindHandler(idx, str(e), conditionStack, loopStack)
                    except Exception as e:
                        self.vars[dest] = None
                        self._print(f"[ERR] {e}")
            elif opcode == OPCODE_FWRITE:
                path, pos = self._readValue(data, pos)
                content, pos = self._readValue(data, pos)
                if executing:
                    try:
                        p = self._sandboxPath(str(path or ""))
                        if isProtectedManualPath is not None and isProtectedManualPath(p):
                            raise PermissionError("protected path")
                        if p.name == PROFILE_FILE:
                            raise PermissionError("protected file")
                        p.parent.mkdir(parents=True, exist_ok=True)
                        p.write_text(str(content or ""), encoding="utf-8")
                    except PermissionError as e:
                        idx = self._findHandler(data, pos, end, pos)
                        if idx is None:
                            self._print(f"[ERR] {e}")
                        else:
                            pos = self._bindHandler(idx, str(e), conditionStack, loopStack)
                    except Exception as e:
                        self._print(f"[ERR] {e}")
            elif opcode == OPCODE_FAPPEND:
                path, pos = self._readValue(data, pos)
                content, pos = self._readValue(data, pos)
                if executing:
                    try:
                        p = self._sandboxPath(str(path or ""))
                        if isProtectedManualPath is not None and isProtectedManualPath(p):
                            raise PermissionError("protected path")
                        if p.name == PROFILE_FILE:
                            raise PermissionError("protected file")
                        with open(p, "a", encoding="utf-8") as f:
                            f.write(str(content or ""))
                    except PermissionError as e:
                        idx = self._findHandler(data, pos, end, pos)
                        if idx is None:
                            self._print(f"[ERR] {e}")
                        else:
                            pos = self._bindHandler(idx, str(e), conditionStack, loopStack)
                    except Exception as e:
                        self._print(f"[ERR] {e}")
            elif opcode == OPCODE_FDELETE:
                path, pos = self._readValue(data, pos)
                if executing:
                    try:
                        p = self._sandboxPath(str(path or ""))
                        if isProtectedManualPath is not None and isProtectedManualPath(p):
                            raise PermissionError("protected path")
                        if p.name == PROFILE_FILE:
                            raise PermissionError("protected file")
                        if p.exists():
                            p.unlink()
                    except PermissionError as e:
                        idx = self._findHandler(data, pos, end, pos)
                        if idx is None:
                            self._print(f"[ERR] {e}")
                        else:
                            pos = self._bindHandler(idx, str(e), conditionStack, loopStack)
                    except Exception as e:
                        self._print(f"[ERR] {e}")
            elif opcode == OPCODE_FEXISTS:
                dest, pos = self._readToken(data, pos)
                path, pos = self._readValue(data, pos)
                if executing:
                    try:
                        p = self._sandboxPath(str(path or ""))
                        self.vars[dest] = p.exists()
                    except PermissionError as e:
                        idx = self._findHandler(data, pos, end, pos)
                        if idx is None:
                            self.vars[dest] = False
                        else:
                            pos = self._bindHandler(idx, str(e), conditionStack, loopStack)
                    except Exception:
                        self.vars[dest] = False
            elif opcode == OPCODE_MKDIR:
                path, pos = self._readValue(data, pos)
                if executing:
                    try:
                        p = self._sandboxPath(str(path or ""))
                        if isProtectedManualPath is not None and isProtectedManualPath(p):
                            raise PermissionError("protected path")
                        if p.name == PROFILE_FILE:
                            raise PermissionError("protected file")
                        p.mkdir(parents=True, exist_ok=True)
                    except PermissionError as e:
                        idx = self._findHandler(data, pos, end, pos)
                        if idx is None:
                            self._print(f"[ERR] {e}")
                        else:
                            pos = self._bindHandler(idx, str(e), conditionStack, loopStack)
                    except Exception as e:
                        self._print(f"[ERR] {e}")
            elif opcode == OPCODE_FREADLINE:
                dest, pos = self._readToken(data, pos)
                path, pos = self._readValue(data, pos)
                idx, pos = self._readValue(data, pos)
                if executing:
                    try:
                        p = self._sandboxPath(str(path or ""))
                        content = p.read_text(encoding="utf-8") if p.exists() else ""
                        self.vars[dest] = FsModule.readLineContent(content, idx)
                    except PermissionError as e:
                        idx = self._findHandler(data, pos, end, pos)
                        if idx is None:
                            self.vars[dest] = None
                            self._print(f"[ERR] {e}")
                        else:
                            pos = self._bindHandler(idx, str(e), conditionStack, loopStack)
                    except Exception as e:
                        self.vars[dest] = None
                        self._print(f"[ERR] {e}")
            elif opcode == OPCODE_FWRITELINE:
                path, pos = self._readValue(data, pos)
                idx, pos = self._readValue(data, pos)
                content, pos = self._readValue(data, pos)
                if executing:
                    try:
                        p = self._sandboxPath(str(path or ""))
                        if isProtectedManualPath is not None and isProtectedManualPath(p):
                            raise PermissionError("protected path")
                        if p.name == PROFILE_FILE:
                            raise PermissionError("protected file")
                        lines = p.read_text(encoding="utf-8").splitlines() if p.exists() else []
                        i = int(idx or 0)
                        while len(lines) <= i:
                            lines.append("")
                        lines[i] = str(content or "")
                        p.parent.mkdir(parents=True, exist_ok=True)
                        p.write_text("\n".join(lines), encoding="utf-8")
                    except PermissionError as e:
                        idx = self._findHandler(data, pos, end, pos)
                        if idx is None:
                            self._print(f"[ERR] {e}")
                        else:
                            pos = self._bindHandler(idx, str(e), conditionStack, loopStack)
                    except Exception as e:
                        self._print(f"[ERR] {e}")
            elif opcode == OPCODE_FLEN:
                dest, pos = self._readToken(data, pos)
                path, pos = self._readValue(data, pos)
                if executing:
                    try:
                        p = self._sandboxPath(str(path or ""))
                        content = p.read_text(encoding="utf-8") if p.exists() else ""
                        self.vars[dest] = FsModule.getLength(content)
                    except PermissionError as e:
                        idx = self._findHandler(data, pos, end, pos)
                        if idx is None:
                            self.vars[dest] = 0
                        else:
                            pos = self._bindHandler(idx, str(e), conditionStack, loopStack)
                    except Exception:
                        self.vars[dest] = 0
            elif opcode == OPCODE_PATHJOIN:
                dest, pos = self._readToken(data, pos)
                a, pos = self._readValue(data, pos)
                b, pos = self._readValue(data, pos)
                if executing:
                    self.vars[dest] = FsModule.joinPaths(a, b)
            elif opcode == OPCODE_PATHBASE:
                dest, pos = self._readToken(data, pos)
                v, pos = self._readValue(data, pos)
                if executing:
                    self.vars[dest] = FsModule.baseName(v)
            elif opcode == OPCODE_PATHDIR:
                dest, pos = self._readToken(data, pos)
                v, pos = self._readValue(data, pos)
                if executing:
                    self.vars[dest] = FsModule.dirName(v)
            elif opcode == OPCODE_PATHEXISTS:
                dest, pos = self._readToken(data, pos)
                v, pos = self._readValue(data, pos)
                if executing:
                    try:
                        p = self._sandboxPath(str(v or ""))
                        self.vars[dest] = p.exists()
                    except PermissionError as e:
                        idx = self._findHandler(data, pos, end, pos)
                        if idx is None:
                            self.vars[dest] = False
                        else:
                            pos = self._bindHandler(idx, str(e), conditionStack, loopStack)
                    except Exception:
                        self.vars[dest] = False
            elif opcode == OPCODE_FLIST:
                dest, pos = self._readToken(data, pos)
                v, pos = self._readValue(data, pos)
                if executing:
                    try:
                        p = self._sandboxPath(str(v or ""))
                        names = [x.name for x in p.iterdir()] if p.exists() and p.is_dir() else []
                        self.vars[dest] = names
                    except PermissionError as e:
                        idx = self._findHandler(data, pos, end, pos)
                        if idx is None:
                            self.vars[dest] = []
                        else:
                            pos = self._bindHandler(idx, str(e), conditionStack, loopStack)
                    except Exception:
                        self.vars[dest] = []
            elif opcode == OPCODE_FCOPY:
                srcName, pos = self._readValue(data, pos)
                dstName, pos = self._readValue(data, pos)
                if executing:
                    try:
                        srcPath = self._sandboxPath(str(srcName or ""))
                        dstPath = self._sandboxPath(str(dstName or ""))
                        if isProtectedManualPath is not None and (isProtectedManualPath(srcPath) or isProtectedManualPath(dstPath)):
                            raise PermissionError("protected path")
                        if srcPath.name == PROFILE_FILE or dstPath.name == PROFILE_FILE:
                            raise PermissionError("protected file")
                        if not srcPath.exists() or not srcPath.is_file():
                            raise FileNotFoundError(f"copy source not found: {srcName}")
                        import shutil
                        dstPath.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(str(srcPath), str(dstPath))
                    except PermissionError as e:
                        idx = self._findHandler(data, pos, end, pos)
                        if idx is None:
                            self._print(f"[ERR] {e}")
                        else:
                            pos = self._bindHandler(idx, str(e), conditionStack, loopStack)
                    except Exception as e:
                        self._print(f"[ERR] {e}")
            elif opcode == OPCODE_FMOVE:
                srcName, pos = self._readValue(data, pos)
                dstName, pos = self._readValue(data, pos)
                if executing:
                    try:
                        srcPath = self._sandboxPath(str(srcName or ""))
                        dstPath = self._sandboxPath(str(dstName or ""))
                        if isProtectedManualPath is not None and (isProtectedManualPath(srcPath) or isProtectedManualPath(dstPath)):
                            raise PermissionError("protected path")
                        if srcPath.name == PROFILE_FILE or dstPath.name == PROFILE_FILE:
                            raise PermissionError("protected file")
                        if not srcPath.exists():
                            raise FileNotFoundError(f"move source not found: {srcName}")
                        import shutil
                        dstPath.parent.mkdir(parents=True, exist_ok=True)
                        shutil.move(str(srcPath), str(dstPath))
                    except PermissionError as e:
                        idx = self._findHandler(data, pos, end, pos)
                        if idx is None:
                            self._print(f"[ERR] {e}")
                        else:
                            pos = self._bindHandler(idx, str(e), conditionStack, loopStack)
                    except Exception as e:
                        self._print(f"[ERR] {e}")
            elif opcode == OPCODE_FSTAT:
                dest, pos = self._readToken(data, pos)
                v, pos = self._readValue(data, pos)
                if executing:
                    try:
                        p = self._sandboxPath(str(v or ""))
                        if not p.exists():
                            self.vars[dest] = None
                        else:
                            st = p.stat()
                            self.vars[dest] = FsModule.statInfo(str(v or ""), p.is_dir(), st.st_size, st.st_mtime)
                    except PermissionError as e:
                        idx = self._findHandler(data, pos, end, pos)
                        if idx is None:
                            self.vars[dest] = None
                            self._print(f"[ERR] {e}")
                        else:
                            pos = self._bindHandler(idx, str(e), conditionStack, loopStack)
                    except Exception:
                        self.vars[dest] = None
            elif opcode == OPCODE_FTOUCH:
                v, pos = self._readValue(data, pos)
                if executing:
                    try:
                        p = self._sandboxPath(str(v or ""))
                        if isProtectedManualPath is not None and isProtectedManualPath(p):
                            raise PermissionError("protected path")
                        if p.name == PROFILE_FILE:
                            raise PermissionError("protected file")
                        p.parent.mkdir(parents=True, exist_ok=True)
                        if not p.exists():
                            p.write_text("", encoding="utf-8")
                    except PermissionError as e:
                        idx = self._findHandler(data, pos, end, pos)
                        if idx is None:
                            self._print(f"[ERR] {e}")
                        else:
                            pos = self._bindHandler(idx, str(e), conditionStack, loopStack)
                    except Exception as e:
                        self._print(f"[ERR] {e}")
            elif opcode == OPCODE_HTTPGET:
                dest, pos = self._readToken(data, pos)
                url, pos = self._readValue(data, pos)
                if executing:
                    try:
                        with urllib.request.urlopen(str(url or ""), timeout=self.httpTimeout) as resp:
                            self.vars[dest] = resp.read().decode("utf-8", errors="replace")
                    except Exception as e:
                        self.vars[dest] = None
                        self._print(f"[ERR] HTTP GET failed: {e}")
            elif opcode == OPCODE_HTTPPOST:
                dest, pos = self._readToken(data, pos)
                url, pos = self._readValue(data, pos)
                body, pos = self._readValue(data, pos)
                if executing:
                    try:
                        data_bytes = str(body or "").encode("utf-8")
                        req = urllib.request.Request(str(url or ""), data=data_bytes, method="POST")
                        with urllib.request.urlopen(req, timeout=self.httpTimeout) as resp:
                            self.vars[dest] = resp.read().decode("utf-8", errors="replace")
                    except Exception as e:
                        self.vars[dest] = None
                        self._print(f"[ERR] HTTP POST failed: {e}")
            elif opcode == OPCODE_HTTPDOWN:
                dest, pos = self._readToken(data, pos)
                url, pos = self._readValue(data, pos)
                if executing:
                    try:
                        savePath = self._sandboxPath(dest)
                        urllib.request.urlretrieve(str(url or ""), str(savePath), timeout=self.httpTimeout)
                        self.vars[dest] = str(savePath)
                    except PermissionError as e:
                        idx = self._findHandler(data, pos, end, pos)
                        if idx is None:
                            self.vars[dest] = None
                            self._print(f"[ERR] {e}")
                        else:
                            pos = self._bindHandler(idx, str(e), conditionStack, loopStack)
                    except Exception as e:
                        self.vars[dest] = None
                        self._print(f"[ERR] HTTP download failed: {e}")
            elif opcode == OPCODE_HTTPFILE:
                dest, pos = self._readToken(data, pos)
                url, pos = self._readValue(data, pos)
                if executing:
                    try:
                        savePath = self._sandboxPath(dest)
                        urllib.request.urlretrieve(str(url or ""), str(savePath), timeout=self.httpTimeout)
                        self.vars[dest] = str(savePath)
                    except PermissionError as e:
                        idx = self._findHandler(data, pos, end, pos)
                        if idx is None:
                            self.vars[dest] = None
                            self._print(f"[ERR] {e}")
                        else:
                            pos = self._bindHandler(idx, str(e), conditionStack, loopStack)
                    except Exception as e:
                        self.vars[dest] = None
                        self._print(f"[ERR] HTTP download failed: {e}")
            elif opcode == OPCODE_ZIP:
                zipName, pos = self._readValue(data, pos)
                srcName, pos = self._readValue(data, pos)
                if executing:
                    try:
                        zipPath = self._sandboxPath(str(zipName or ""))
                        srcPath = self._sandboxPath(str(srcName or ""))
                        if not ZipModule.zipPath(zipPath, srcPath):
                            self._print("[ERR] ZIP failed")
                    except PermissionError as e:
                        idx = self._findHandler(data, pos, end, pos)
                        if idx is None:
                            self._print(f"[ERR] {e}")
                        else:
                            pos = self._bindHandler(idx, str(e), conditionStack, loopStack)
                    except Exception as e:
                        self._print(f"[ERR] {e}")
            elif opcode == OPCODE_UNZIP:
                zipName, pos = self._readValue(data, pos)
                dstName, pos = self._readValue(data, pos)
                if executing:
                    try:
                        zipPath = self._sandboxPath(str(zipName or ""))
                        dstPath = self._sandboxPath(str(dstName or ""))
                        if not ZipModule.unzipPath(zipPath, dstPath):
                            self._print("[ERR] UNZIP failed")
                    except PermissionError as e:
                        idx = self._findHandler(data, pos, end, pos)
                        if idx is None:
                            self._print(f"[ERR] {e}")
                        else:
                            pos = self._bindHandler(idx, str(e), conditionStack, loopStack)
                    except Exception as e:
                        self._print(f"[ERR] {e}")
            elif opcode == OPCODE_JSONPARSE:
                dest, pos = self._readToken(data, pos)
                v, pos = self._readValue(data, pos)
                if executing:
                    self.vars[dest] = JsonModule.parseText(v)
            elif opcode == OPCODE_JSONSTR:
                dest, pos = self._readToken(data, pos)
                v, pos = self._readValue(data, pos)
                if executing:
                    self.vars[dest] = JsonModule.stringifyValue(v)
            elif opcode == OPCODE_JSONGET:
                dest, pos = self._readToken(data, pos)
                j, pos = self._readValue(data, pos)
                k, pos = self._readValue(data, pos)
                if executing:
                    self.vars[dest] = JsonModule.getField(j, k)
            elif opcode == OPCODE_JSONSET:
                dest, pos = self._readToken(data, pos)
                j, pos = self._readValue(data, pos)
                k, pos = self._readValue(data, pos)
                v, pos = self._readValue(data, pos)
                if executing:
                    self.vars[dest] = JsonModule.setField(j, k, v)
            elif opcode == OPCODE_NETINFO:
                dest, pos = self._readToken(data, pos)
                if executing:
                    self.vars[dest] = NetModule.getNetInfo()
            elif opcode == OPCODE_URLENCODE:
                dest, pos = self._readToken(data, pos)
                v, pos = self._readValue(data, pos)
                if executing:
                    self.vars[dest] = NetModule.urlEncodeText(v)
            elif opcode == OPCODE_URLDECODE:
                dest, pos = self._readToken(data, pos)
                v, pos = self._readValue(data, pos)
                if executing:
                    self.vars[dest] = NetModule.urlDecodeText(v)
            elif opcode == OPCODE_HTTPSTATUS:
                dest, pos = self._readToken(data, pos)
                url, pos = self._readValue(data, pos)
                if executing:
                    self.vars[dest] = NetModule.httpStatus(url, self.httpTimeout)
            elif opcode == OPCODE_HTTPTIMEOUT:
                val, pos = self._readValue(data, pos)
                if executing:
                    try:
                        self.httpTimeout = max(float(val or 0), 1)
                    except Exception:
                        self.httpTimeout = 10
            elif opcode == OPCODE_HTTPGETH:
                dest, pos = self._readToken(data, pos)
                url, pos = self._readValue(data, pos)
                headers, pos = self._readValue(data, pos)
                if executing:
                    self.vars[dest] = NetModule.httpGet(url, headers, self.httpTimeout)
                    if self.vars[dest] is None:
                        self._print(f"[ERR] HTTP GET failed: {url}")
            elif opcode == OPCODE_HTTPPOSTH:
                dest, pos = self._readToken(data, pos)
                url, pos = self._readValue(data, pos)
                payload, pos = self._readValue(data, pos)
                if executing:
                    try:
                        import json as jsonMod
                        info = jsonMod.loads(str(payload or ""))
                        body = info.get("body", "") if isinstance(info, dict) else ""
                        headers = info.get("headers", {}) if isinstance(info, dict) else {}
                    except Exception:
                        body = str(payload or "")
                        headers = {}
                    self.vars[dest] = NetModule.httpPost(url, body, headers, self.httpTimeout)
                    if self.vars[dest] is None:
                        self._print(f"[ERR] HTTP POST failed: {url}")
            elif opcode == OPCODE_SOCKCONN:
                dest, pos = self._readToken(data, pos)
                host, pos = self._readValue(data, pos)
                port, pos = self._readValue(data, pos)
                if executing:
                    try:
                        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        s.connect((str(host or ""), int(port or 0)))
                        self.sockets[dest] = s
                        self.vars[dest] = dest
                    except Exception as e:
                        self._print(f"[ERR] Socket connect failed: {e}")
            elif opcode == OPCODE_SOCKSEND:
                sock, pos = self._readValue(data, pos)
                msg, pos = self._readValue(data, pos)
                if executing:
                    key = str(sock or "")
                    if key in self.sockets:
                        try:
                            self.sockets[key].sendall(str(msg or "").encode("utf-8"))
                        except Exception as e:
                            self._print(f"[ERR] Socket send failed: {e}")
            elif opcode == OPCODE_SOCKRECV:
                dest, pos = self._readToken(data, pos)
                if executing:
                    if dest in self.sockets:
                        try:
                            self.vars[dest] = self.sockets[dest].recv(4096).decode("utf-8", errors="replace")
                        except Exception:
                            self.vars[dest] = None
            elif opcode == OPCODE_SOCKCLOSE:
                key, pos = self._readToken(data, pos)
                if executing:
                    if key in self.sockets:
                        try:
                            self.sockets[key].close()
                            del self.sockets[key]
                        except Exception:
                            pass
            elif opcode == OPCODE_OSNAME:
                dest, pos = self._readToken(data, pos)
                if executing:
                    self.vars[dest] = OsModule.getOsName()
            elif opcode == OPCODE_OSARCH:
                dest, pos = self._readToken(data, pos)
                if executing:
                    self.vars[dest] = OsModule.getOsArch()
            elif opcode == OPCODE_OSLANG:
                dest, pos = self._readToken(data, pos)
                if executing:
                    self.vars[dest] = OsModule.getOsLang()
            elif opcode == OPCODE_OSHOST:
                dest, pos = self._readToken(data, pos)
                if executing:
                    self.vars[dest] = OsModule.getHostName()
            elif opcode == OPCODE_SERVERBIND:
                dest, pos = self._readToken(data, pos)
                port, pos = self._readValue(data, pos)
                if executing:
                    try:
                        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                        s.bind(("0.0.0.0", int(port or 0)))
                        self.servers[dest] = s
                        self.vars[dest] = dest
                    except Exception as e:
                        self._print(f"[ERR] Server bind failed: {e}")
            elif opcode == OPCODE_SERVERLSTN:
                val, pos = self._readValue(data, pos)
                if executing:
                    key = str(val or "")
                    if key in self.servers:
                        try:
                            self.servers[key].listen(5)
                        except Exception as e:
                            self._print(f"[ERR] Server listen failed: {e}")
            elif opcode == OPCODE_SERVERACCPT:
                dest, pos = self._readToken(data, pos)
                if executing:
                    if dest in self.servers:
                        try:
                            conn, addr = self.servers[dest].accept()
                            connKey = f"__conn_{dest}"
                            self.sockets[connKey] = conn
                            self.vars[dest] = connKey
                        except Exception as e:
                            self._print(f"[ERR] Server accept failed: {e}")
            elif opcode == OPCODE_SERVERSEND:
                sock, pos = self._readValue(data, pos)
                msg, pos = self._readValue(data, pos)
                if executing:
                    key = str(sock or "")
                    if key in self.sockets:
                        try:
                            self.sockets[key].sendall(str(msg or "").encode("utf-8"))
                        except Exception as e:
                            self._print(f"[ERR] Server send failed: {e}")
            elif opcode == OPCODE_SERVERRECV:
                dest, pos = self._readToken(data, pos)
                if executing:
                    key = str(self.vars.get(dest, dest))
                    if key in self.sockets:
                        try:
                            self.vars[dest] = self.sockets[key].recv(4096).decode("utf-8", errors="replace")
                        except Exception:
                            self.vars[dest] = None
            elif opcode == OPCODE_SERVERCLS:
                key, pos = self._readToken(data, pos)
                if executing:
                    if key in self.servers:
                        try:
                            self.servers[key].close()
                            del self.servers[key]
                        except Exception:
                            pass
            elif opcode == OPCODE_DATE:
                dest, pos = self._readToken(data, pos)
                if executing:
                    self.vars[dest] = DataModule.getDate()
            elif opcode == OPCODE_DATEDMY:
                dest, pos = self._readToken(data, pos)
                if executing:
                    self.vars[dest] = DataModule.getDateDmy()
            elif opcode == OPCODE_WEEKDAY:
                dest, pos = self._readToken(data, pos)
                if executing:
                    self.vars[dest] = DataModule.getWeekday()
            elif opcode == OPCODE_DAYOFYEAR:
                dest, pos = self._readToken(data, pos)
                if executing:
                    self.vars[dest] = DataModule.getDayOfYear()
            elif opcode == OPCODE_MONTH:
                dest, pos = self._readToken(data, pos)
                if executing:
                    self.vars[dest] = DataModule.getMonth()
            elif opcode == OPCODE_YEAR:
                dest, pos = self._readToken(data, pos)
                if executing:
                    self.vars[dest] = DataModule.getYear()
            elif opcode == OPCODE_DAY:
                dest, pos = self._readToken(data, pos)
                if executing:
                    self.vars[dest] = DataModule.getDay()
            elif opcode == OPCODE_TIME:
                dest, pos = self._readToken(data, pos)
                if executing:
                    self.vars[dest] = TimeModule.getTime()
            elif opcode == OPCODE_HOUR:
                dest, pos = self._readToken(data, pos)
                if executing:
                    self.vars[dest] = TimeModule.getHour()
            elif opcode == OPCODE_MINUTE:
                dest, pos = self._readToken(data, pos)
                if executing:
                    self.vars[dest] = TimeModule.getMinute()
            elif opcode == OPCODE_SECOND:
                dest, pos = self._readToken(data, pos)
                if executing:
                    self.vars[dest] = TimeModule.getSecond()
            elif opcode == OPCODE_TIMESTAMP:
                dest, pos = self._readToken(data, pos)
                if executing:
                    self.vars[dest] = TimeModule.getTimestamp()
            elif opcode == OPCODE_SLEEP:
                val, pos = self._readValue(data, pos)
                if executing:
                    ScheduleModule.sleepSeconds(val)
            elif opcode == OPCODE_FPS:
                dest, pos = self._readToken(data, pos)
                if executing:
                    self.vars[dest] = ScheduleModule.getFps()
            elif opcode == OPCODE_TICK:
                dest, pos = self._readToken(data, pos)
                if executing:
                    self.vars[dest] = ScheduleModule.getTick()
            elif opcode == OPCODE_SCHEDULE:
                dest, pos = self._readToken(data, pos)
                val, pos = self._readValue(data, pos)
                if executing:
                    try:
                        self.vars[dest] = float(val or 0)
                    except Exception:
                        self.vars[dest] = 0
            elif opcode == OPCODE_ARGS:
                dest, pos = self._readToken(data, pos)
                if executing:
                    self.vars[dest] = self.args
            elif opcode == OPCODE_ARGGET:
                dest, pos = self._readToken(data, pos)
                idx, pos = self._readValue(data, pos)
                if executing:
                    try:
                        i = int(idx or 0)
                        self.vars[dest] = self.args[i] if 0 <= i < len(self.args) else None
                    except Exception:
                        self.vars[dest] = None
            elif opcode == OPCODE_ARGLEN:
                dest, pos = self._readToken(data, pos)
                if executing:
                    self.vars[dest] = len(self.args)
            elif opcode == OPCODE_RANDINT:
                dest, pos = self._readToken(data, pos)
                a, pos = self._readValue(data, pos)
                b, pos = self._readValue(data, pos)
                if executing:
                    self.vars[dest] = RandomModule.randomInt(a, b)
            elif opcode == OPCODE_RANDSTR:
                dest, pos = self._readToken(data, pos)
                n, pos = self._readValue(data, pos)
                chars, pos = self._readValue(data, pos)
                if executing:
                    self.vars[dest] = RandomModule.randomString(n, chars)
            elif opcode == OPCODE_RANDCHOICE:
                dest, pos = self._readToken(data, pos)
                lst, pos = self._readValue(data, pos)
                if executing:
                    self.vars[dest] = RandomModule.randomChoice(lst)
            elif opcode == OPCODE_UUID:
                dest, pos = self._readToken(data, pos)
                if executing:
                    self.vars[dest] = UuidModule.newUuid()
            elif opcode == OPCODE_HASH:
                dest, pos = self._readToken(data, pos)
                v, pos = self._readValue(data, pos)
                if executing:
                    self.vars[dest] = HashModule.hashText(v)
            elif opcode == OPCODE_HASHSHA256:
                dest, pos = self._readToken(data, pos)
                v, pos = self._readValue(data, pos)
                if executing:
                    self.vars[dest] = HashModule.hashSha256(v)
            elif opcode == OPCODE_HASHMD5:
                dest, pos = self._readToken(data, pos)
                v, pos = self._readValue(data, pos)
                if executing:
                    self.vars[dest] = HashModule.hashMd5(v)
            elif opcode == OPCODE_ENCRYPT:
                dest, pos = self._readToken(data, pos)
                v, pos = self._readValue(data, pos)
                k, pos = self._readValue(data, pos)
                if executing:
                    self.vars[dest] = EncryptModule.encryptText(v, k)
            elif opcode == OPCODE_DECRYPT:
                dest, pos = self._readToken(data, pos)
                v, pos = self._readValue(data, pos)
                k, pos = self._readValue(data, pos)
                if executing:
                    self.vars[dest] = EncryptModule.decryptText(v, k)
            elif opcode == OPCODE_IMPORT:
                nameVal, pos = self._readValue(data, pos)
                if executing and nameVal:
                    self.importModule(str(nameVal))
            elif opcode == OPCODE_SHELLEXEC:
                dest, pos = self._readToken(data, pos)
                cmd, pos = self._readValue(data, pos)
                if executing:
                    if not self.isSudo:
                        idx = self._findHandler(data, pos, end, pos)
                        if idx is None:
                            self.vars[dest] = None
                            self._print(f"[ERR] SHELLEXEC: permission denied (requires sudo)")
                        else:
                            self.vars[dest] = None
                            pos = self._bindHandler(idx, "SHELLEXEC: permission denied (requires sudo)", conditionStack, loopStack)
                    else:
                        try:
                            proc = subprocess.run(str(cmd or ""), shell=True, capture_output=True, text=True)
                            self.vars[dest] = proc.stdout + proc.stderr
                        except Exception as e:
                            self.vars[dest] = None
                            self._print(f"[ERR] SHELLEXEC: {e}")
            elif opcode == OPCODE_EXIT:
                if executing:
                    return pos
            elif opcode == 0xF1:
                val, pos = self._readValue(data, pos)
                if executing:
                    self._print(val if val is not None else "")
            elif opcode == 0xF2:
                val, pos = self._readValue(data, pos)
                if executing:
                    self._print(val if val is not None else "")
            elif opcode == 0xF3:
                val, pos = self._readValue(data, pos)
                if executing:
                    self._print(val if val is not None else "")
            elif opcode == 0xF4:
                dest, pos = self._readToken(data, pos)
                if executing:
                    self.vars[dest] = bool(self.isSudo)
            else:
                handled = self.handleExtension(opcode, data, pos, end, executing)
                if handled is not None:
                    pos = handled
                else:
                    try:
                        pos = self._skipInstruction(data, pos - 1 + 1, opcode)
                    except Exception:
                        pass
        return pos
    def _fromHexFile(self, content: str) -> bytes:
        result = bytearray()
        for line in content.splitlines():
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            if len(parts) < 2:
                continue
            hexBytes = parts[1:]
            for h in hexBytes:
                try:
                    result.append(int(h, 16))
                except ValueError:
                    pass
        return bytes(result)
