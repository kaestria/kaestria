import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from bin.shared.Interpreter import SharedInterpreter
from bin.appcommand.command.CommandModule import CommandModule
from bin.appcommand.logger.LoggerModule import LoggerModule
class AppCommandInterpreter(SharedInterpreter):
    def __init__(self, programName: str = None, isSudo: bool = False, vistroRoot: Path = None, username: str = None, role: str = None):
        super().__init__(programName, isSudo, vistroRoot, username, role)
    def getCommandLength(self) -> int:
        return CommandModule.getLength(self.args)
    def getCommandArgument(self, index):
        return CommandModule.getArgument(self.args, index)
    def logInfo(self, msg):
        self._print(LoggerModule.formatInfo(msg))
    def logWarn(self, msg):
        self._print(LoggerModule.formatWarn(msg))
    def logError(self, msg):
        self._print(LoggerModule.formatError(msg))
    def isSudoEnabled(self) -> bool:
        return bool(self.isSudo)
