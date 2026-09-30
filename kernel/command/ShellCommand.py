import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from bin.shell.converter.Loader import listShells, findShellFile
from bin.shell.session import Session as ShellSession
import subprocess
def cmdShell(args: list, session) -> str:
    if not args:
        return (
            "Usage: shell <-S|-L|-Q>\n"
            "  shell -S <name> - Start shell\n"
            "  shell -L - List shells\n"
            "  shell -Q [name] - Quit shell"
        )
    flag = args[0]
    if flag == "-L":
        shells = listShells()
        if not shells:
            return "(no shells)"
        return "\n".join(shells)
    if flag == "-S":
        if len(args) < 2:
            return "shell: missing shell name"
        name = args[1]
        target = findShellFile(name)
        if target is None:
            return f"shell: {name}: not found"
        display = target.stem
        hostPath = str(Path(__file__).resolve().parents[2] / "bin" / "shell" / "converter" / "Host.py")
        try:
            proc = subprocess.Popen(
                [sys.executable, hostPath, display] + args[2:],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
        except Exception as e:
            return f"shell: failed to start: {e}"
        session.addShell(display, {"path": str(target), "pid": proc.pid})
        return (
            f"Decompiling {display}... [100%]\n"
            f"Loading {display}... [100%]\n"
            f"Starting {display}... (PID {proc.pid})"
        )
    if flag == "-Q":
        if len(args) >= 2:
            name = args[1]
            active = session.listShells()
            target = None
            for entry in active:
                if entry.lower() == str(name).lower():
                    target = entry
                    break
            if target is None:
                return f"shell: {name}: not running"
            info = session.getShell(target) or {}
            stopPid(info.get("pid"))
            session.removeShell(target)
            ShellSession.clearShellTokens(target)
            return f"Stopped {target}"
        active = session.listShells()
        for entry in list(active):
            info = session.getShell(entry) or {}
            stopPid(info.get("pid"))
            session.removeShell(entry)
            ShellSession.clearShellTokens(entry)
        return "Stopped all shells"
    return f"shell: unknown flag {flag}"
def stopPid(pid) -> bool:
    try:
        if pid is None:
            return False
        import os
        import signal
        os.kill(int(pid), signal.SIGTERM)
        return True
    except Exception:
        return False
