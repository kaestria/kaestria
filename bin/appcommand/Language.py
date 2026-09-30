import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from bin.shared.Language import Compiler as SharedCompiler, fromHexFile as sharedFromHex, MNEMONIC_MAP as SHARED_MAP
OPCODE_LOG = 0xF1
OPCODE_LOGWARN = 0xF2
OPCODE_LOGERR = 0xF3
OPCODE_SUDOCHECK = 0xF4
APP_MNEMONIC_MAP = dict(SHARED_MAP)
APP_MNEMONIC_MAP.update({
    "LOG": OPCODE_LOG,
    "LOGWARN": OPCODE_LOGWARN,
    "LOGERR": OPCODE_LOGERR,
    "SUDOCHECK": OPCODE_SUDOCHECK,
    "CMDLOG": OPCODE_LOG,
})
class AppCompiler(SharedCompiler):
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
        if mnemonic == "IMPORT":
            self.errors.append("IMPORT allowed only in shells")
            return
        if mnemonic in ("LOG", "LOGWARN", "LOGERR", "CMDLOG"):
            opcode = APP_MNEMONIC_MAP[mnemonic]
            self._emit(opcode)
            val = " ".join(args)
            vt, vv = self._parseValue(val)
            self._emitValue(vt, vv)
            return
        if mnemonic == "SUDOCHECK":
            self._emit(OPCODE_SUDOCHECK)
            if args:
                self._emitBytes(__import__("struct").pack(">H", len(args[0].encode())) + args[0].encode())
            return
        if mnemonic not in APP_MNEMONIC_MAP:
            self.errors.append(f"Unknown mnemonic: {mnemonic}")
            return
        super().compileLine(line)
def compileSource(source: str) -> str:
    c = AppCompiler()
    bytecode = c.compile(source)
    return c.toHexFile(bytecode)
def fromHexFile(content: str) -> bytes:
    return sharedFromHex(content)
def runAppCommand(hexContent: str, args: list = None, programName: str = None, isSudo: bool = False, username: str = None, role: str = None) -> str:
    from bin.appcommand.Interpreter import AppCommandInterpreter
    bytecode = fromHexFile(hexContent)
    try:
        from kernel.system.Constant import VISTRO_ROOT
        root = VISTRO_ROOT
    except Exception:
        root = Path.home() / "vistro" / "root"
    interp = AppCommandInterpreter(programName, isSudo=isSudo, vistroRoot=root, username=username, role=role)
    return interp.execute(bytecode, args or [])
