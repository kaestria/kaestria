import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from kernel.system.Constant import VISTRO_PROGRAMS, VISTRO_DATA, APP_COMMAND_FILE
from kernel.command.Commands import cmdCd, cmdPwd, cmdDir, cmdCat, cmdMkdir, cmdClear, cmdWhoami, cmdFetch, cmdHelp, cmdRm, cmdCp, cmdMv, cmdUser, cmdInstall, cmdUninstall, cmdSudo
from kernel.command.ShellCommand import cmdShell
from fs.Sandbox import resolvePath, isInsideSandbox
from bin.appcommand.Language import runAppCommand
BUILTIN_COMMANDS = {
    "cd": cmdCd,
    "pwd": cmdPwd,
    "ls": cmdDir,
    "cat": cmdCat,
    "mkdir": cmdMkdir,
    "clear": cmdClear,
    "cls": cmdClear,
    "whoami": cmdWhoami,
    "fetch": cmdFetch,
    "help": cmdHelp,
    "rm": cmdRm,
    "del": cmdRm,
    "cp": cmdCp,
    "mv": cmdMv,
    "user": cmdUser,
    "install": cmdInstall,
    "uninstall": cmdUninstall,
    "shell": cmdShell,
    "sudo": cmdSudo,
}
def dispatch(line: str, session) -> str:
    line = line.strip()
    if not line:
        return ""
    pendingUninstall = session.getPendingUninstall()
    if pendingUninstall is not None:
        session.clearPendingUninstall()
        if line.lower() == "y":
            import shutil
            appName = pendingUninstall.get("appName", "")
            programDir = VISTRO_PROGRAMS / appName
            dataDir = VISTRO_DATA / appName
            try:
                if programDir.exists():
                    shutil.rmtree(programDir)
                if dataDir.exists():
                    shutil.rmtree(dataDir)
                return f"Uninstalled '{appName}'"
            except Exception as e:
                return f"uninstall: {e}"
        return "uninstall: aborted"
    pending = session.getPendingSudo()
    if pending is not None:
        session.clearPendingSudo()
        if line.lower() == "y":
            from bin.appcommand.Language import runAppCommand
            return runAppCommand(pending["content"], pending["args"], programName=pending["programName"], isSudo=True, username=session.getUsername(), role=session.getRole())
        return "sudo: aborted"
    parts = _tokenize(line)
    if not parts:
        return ""
    command = parts[0].lower()
    args = parts[1:]
    if command in BUILTIN_COMMANDS:
        try:
            return BUILTIN_COMMANDS[command](args, session)
        except Exception as e:
            return f"{command}: error: {e}"
    result = _tryRunAppCommand(command, args, session)
    if result is not None:
        return result
    directPath = resolvePath(session.getCurrentPath(), parts[0])
    if isInsideSandbox(directPath) and directPath.exists() and directPath.suffix == ".AppCommand":
        try:
            content = directPath.read_text(encoding="utf-8")
            return runAppCommand(content, args, programName=None, username=session.getUsername(), role=session.getRole())
        except Exception as e:
            return f"Error executing {parts[0]}: {e}"
    return f"{command}: command not found"
def _tryRunAppCommand(commandName: str, args: list, session) -> str | None:
    programDir = VISTRO_PROGRAMS / commandName
    if not programDir.exists():
        capitalized = commandName.capitalize()
        programDir = VISTRO_PROGRAMS / capitalized
        if not programDir.exists() and VISTRO_PROGRAMS.exists():
            lowered = commandName.lower()
            for entry in VISTRO_PROGRAMS.iterdir():
                if entry.is_dir() and entry.name.lower() == lowered:
                    programDir = entry
                    break
        if not programDir.exists():
            return None
    cmdFile = programDir / APP_COMMAND_FILE
    if not cmdFile.exists():
        return None
    try:
        content = cmdFile.read_text(encoding="utf-8")
        allArgs = [commandName] + args
        return runAppCommand(content, allArgs, programName=programDir.name, username=session.getUsername(), role=session.getRole())
    except Exception as e:
        return f"{commandName}: runtime error: {e}"
def _tokenize(line: str) -> list:
    tokens = []
    current = ""
    inQuote = False
    quoteChar = ""
    for c in line:
        if inQuote:
            if c == quoteChar:
                inQuote = False
            else:
                current += c
        elif c in ('"', "'"):
            inQuote = True
            quoteChar = c
        elif c == " ":
            if current:
                tokens.append(current)
                current = ""
        else:
            current += c
    if current:
        tokens.append(current)
    return tokens
