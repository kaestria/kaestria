import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from bin.shared.Language import Compiler as SharedCompiler, fromHexFile as sharedFromHex, MNEMONIC_MAP as SHARED_MAP, compileSource as sharedCompileSource
OPCODE_LOGIN = 0x14
OPCODE_LOGOUT = 0x15
OPCODE_TOKENSET = 0x16
OPCODE_TOKENCLEAR = 0x17
OPCODE_TOKENUSER = 0x18
OPCODE_INPUT = 0x19
OPCODE_WINCREATE = 0x22
OPCODE_WINSET = 0x23
OPCODE_WINCLOSE = 0x24
OPCODE_UICREATE = 0x25
OPCODE_UISET = 0x26
OPCODE_UIGET = 0x27
OPCODE_UION = 0x28
OPCODE_UIBLUR = 0x29
OPCODE_UICURSOR = 0x2A
OPCODE_UISOUND = 0x2B
OPCODE_UIWEB = 0x2C
OPCODE_UICLEAR = 0x2D
SHELL_MNEMONIC_MAP = dict(SHARED_MAP)
SHELL_MNEMONIC_MAP.update({
    "LOGIN": OPCODE_LOGIN,
    "LOGOUT": OPCODE_LOGOUT,
    "TOKENSET": OPCODE_TOKENSET,
    "TOKENCLEAR": OPCODE_TOKENCLEAR,
    "TOKENUSER": OPCODE_TOKENUSER,
    "INPUT": OPCODE_INPUT,
    "WINCREATE": OPCODE_WINCREATE,
    "WINSET": OPCODE_WINSET,
    "WINCLOSE": OPCODE_WINCLOSE,
    "UICREATE": OPCODE_UICREATE,
    "UISET": OPCODE_UISET,
    "UIGET": OPCODE_UIGET,
    "UION": OPCODE_UION,
    "UIBLUR": OPCODE_UIBLUR,
    "UICURSOR": OPCODE_UICURSOR,
    "UISOUND": OPCODE_UISOUND,
    "UIWEB": OPCODE_UIWEB,
    "UICLEAR": OPCODE_UICLEAR,
})
class ShellCompiler(SharedCompiler):
    def compileLine(self, line: str):
        import re
        line = re.sub(r'<!--.*?-->', '', line).strip()
        if not line:
            return
        parts = self._tokenize(line)
        if not parts:
            return
        mnemonic = parts[0].upper()
        args = parts[1:]
        if mnemonic not in SHELL_MNEMONIC_MAP:
            self.errors.append(f"Unknown mnemonic: {mnemonic}")
            return
        opcode = SHELL_MNEMONIC_MAP[mnemonic]
        if opcode not in (OPCODE_LOGIN, OPCODE_LOGOUT, OPCODE_TOKENSET, OPCODE_TOKENCLEAR, OPCODE_TOKENUSER, OPCODE_INPUT, OPCODE_WINCREATE, OPCODE_WINSET, OPCODE_WINCLOSE, OPCODE_UICREATE, OPCODE_UISET, OPCODE_UIGET, OPCODE_UION, OPCODE_UIBLUR, OPCODE_UICURSOR, OPCODE_UISOUND, OPCODE_UIWEB, OPCODE_UICLEAR):
            super().compileLine(line)
            return
        self._emit(opcode)
        if mnemonic == "LOGIN":
            if len(args) >= 3:
                self._emitBytes(self._encodeTokenPublic(args[0]))
                vt1, vv1 = self._parseValue(args[1])
                self._emitValue(vt1, vv1)
                vt2, vv2 = self._parseValue(" ".join(args[2:]))
                self._emitValue(vt2, vv2)
        elif mnemonic in ("LOGOUT", "TOKENSET", "WINCLOSE", "UICURSOR", "UISOUND", "UICLEAR"):
            val = " ".join(args)
            vt, vv = self._parseValue(val)
            self._emitValue(vt, vv)
        elif mnemonic == "TOKENCLEAR":
            pass
        elif mnemonic in ("TOKENUSER", "INPUT", "WINCREATE"):
            self._emitDestSingle(args)
        elif mnemonic in ("UICREATE", "UIWEB", "UIBLUR", "UIGET"):
            self._emitDestDouble(args)
        elif mnemonic in ("WINSET", "UISET", "UION", "UIGET"):
            if mnemonic == "UIGET":
                if len(args) >= 3:
                    self._emitBytes(self._encodeTokenPublic(args[0]))
                    vt1, vv1 = self._parseValue(args[1])
                    self._emitValue(vt1, vv1)
                    self._emitValue("str", self._literalText(args[2]))
            elif len(args) >= 3:
                vt1, vv1 = self._parseValue(args[0])
                self._emitValue(vt1, vv1)
                self._emitValue("str", self._literalText(args[1]))
                if mnemonic == "UION":
                    self._emitValue("str", self._literalText(" ".join(args[2:])))
                else:
                    vt3, vv3 = self._parseValue(" ".join(args[2:]))
                    self._emitValue(vt3, vv3)
    def _literalText(self, tok: str) -> str:
        t = tok.strip()
        if len(t) >= 2 and t.startswith('"') and t.endswith('"'):
            return t[1:-1]
        return t
    def _encodeTokenPublic(self, tok: str) -> bytes:
        import struct
        data = tok.encode("utf-8")
        return struct.pack(">H", len(data)) + data
def compileSource(source: str) -> str:
    c = ShellCompiler()
    bytecode = c.compile(source)
    return c.toHexFile(bytecode)
def fromHexFile(content: str) -> bytes:
    return sharedFromHex(content)
def runShell(bytecode: bytes, args: list = None, shellName: str = None, modules: dict = None, vistroRoot=None, username: str = None, role: str = None) -> str:
    from bin.shell.Interpreter import ShellInterpreter
    interp = ShellInterpreter(shellName or "", modules=modules or {}, vistroRoot=vistroRoot, username=username, role=role)
    return interp.execute(bytecode, args or [])
