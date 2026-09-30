import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from kernel.system.Constant import VISTRO_ROOT, VISTRO_PROGRAMS, VISTRO_USERS, VISTRO_DATA, APP_COMMAND_FILE, APP_MANIFEST_FILE, APP_INSTALLER_EXT, PROFILE_FILE, ADMIN_USER, HASH_ALGORITHM
from fs.Sandbox import resolvePath, isInsideSandbox, canDelete, canAccess, canManualMkdir, canManualRemove, canManualCopy, canManualMove, safeJoin, isSafeMemberName
from kernel.user.UserManager import createUser, deleteUser, listUsers, getProfile, changePassword, userExists, hashPassword
import os
import shutil
import fnmatch
import json
import zipfile
import hashlib
def cmdCd(args: list, session) -> str:
    if not args:
        session.setCurrentPath(VISTRO_ROOT)
        return ""
    target = args[0]
    resolved = resolvePath(session.getCurrentPath(), target)
    if not isInsideSandbox(resolved):
        return f"cd: access denied: outside sandbox"
    if not resolved.exists():
        return f"cd: {args[0]}: No such file or directory"
    if not resolved.is_dir():
        return f"cd: {args[0]}: Not a directory"
    session.setCurrentPath(resolved)
    return ""
def cmdPwd(args: list, session) -> str:
    try:
        rel = session.getCurrentPath().relative_to(VISTRO_ROOT.parent.parent)
        return "~/" + str(rel).replace("\\", "/")
    except ValueError:
        return str(session.getCurrentPath())
def cmdDir(args: list, session) -> str:
    pattern = args[0] if args else "*"
    target = session.getCurrentPath()
    if "/" in pattern or "\\" in pattern:
        parts = pattern.replace("\\", "/").rsplit("/", 1)
        target = resolvePath(session.getCurrentPath(), parts[0])
        pattern = parts[1] if len(parts) > 1 else "*"
    if not isInsideSandbox(target):
        return "ls: access denied"
    if not target.exists():
        return f"ls: {target}: No such directory"
    entries = sorted(target.iterdir(), key=lambda x: (x.is_file(), x.name.lower()))
    result = []
    for entry in entries:
        if fnmatch.fnmatch(entry.name, pattern):
            marker = "/" if entry.is_dir() else ""
            result.append(f"{entry.name}{marker}")
    return "\n".join(result) if result else "(empty)"
def cmdCat(args: list, session) -> str:
    if not args:
        return "cat: missing operand"
    pattern = args[0]
    target = session.getCurrentPath()
    if "/" in pattern or "\\" in pattern:
        parts = pattern.replace("\\", "/").rsplit("/", 1)
        target = resolvePath(session.getCurrentPath(), parts[0])
        pattern = parts[1]
    if not isInsideSandbox(target):
        return "cat: access denied"
    matches = [f for f in target.iterdir() if fnmatch.fnmatch(f.name, pattern) and f.is_file()]
    if not matches:
        return f"cat: {args[0]}: No such file"
    results = []
    for f in matches:
        if not canAccess(f, session.getUsername(), session.getRole()):
            results.append(f"cat: {f.name}: Permission denied")
            continue
        try:
            results.append(f.read_text(encoding="utf-8"))
        except Exception as e:
            results.append(f"cat: {f.name}: {e}")
    return "\n".join(results)
def cmdMkdir(args: list, session) -> str:
    if not args:
        return "mkdir: missing operand"
    results = []
    for arg in args:
        target = resolvePath(session.getCurrentPath(), arg)
        if not isInsideSandbox(target):
            results.append(f"mkdir: {arg}: access denied")
            continue
        if not canManualMkdir(target):
            results.append(f"mkdir: {arg}: protected path: use install or user create")
            continue
        if not canAccess(target.parent, session.getUsername(), session.getRole()):
            results.append(f"mkdir: {arg}: Permission denied")
            continue
        try:
            target.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            results.append(f"mkdir: {arg}: {e}")
    return "\n".join(results)
def cmdClear(args: list, session) -> str:
    return "\033[2J\033[H"
def cmdWhoami(args: list, session) -> str:
    return f"{session.getUsername()} ({session.getRole()})"
def cmdFetch(args: list, session) -> str:
    from kernel.fetch.Fetch import run
    return run(session)
def cmdHelp(args: list, session) -> str:
    return (
        "Built-in commands:\n"
        "  cd [path]         - Change directory\n"
        "  pwd               - Print working directory\n"
        "  ls [pattern]      - List directory contents\n"
        "  cat <file>        - Print file contents\n"
        "  mkdir <dir>       - Create directory\n"
        "  rm <path>         - Remove file or directory\n"
        "  cp <src> <dst>    - Copy file\n"
        "  mv <src> <dst>    - Move/rename file\n"
        "  fetch             - Show system info\n"
        "  clear             - Clear screen\n"
        "  whoami            - Show current user\n"
        "  user <action>     - Manage users (create|delete|list|passwd)\n"
        "  install <file>    - Install .AppInstaller package\n"
        "  uninstall <app>   - Remove installed program\n"
        "  shell <flag>      - Manage shells (-S|-L|-Q)\n"
        "  sudo <program>    - Run a program's .AppCommand in the real OS konsole (admin only)\n"
        "  help              - Show this help"
    )
def cmdRm(args: list, session) -> str:
    if not args:
        return "rm: missing operand"
    results = []
    for arg in args:
        target = resolvePath(session.getCurrentPath(), arg)
        if not isInsideSandbox(target):
            results.append(f"rm: {arg}: access denied")
            continue
        if not canManualRemove(target):
            results.append(f"rm: {arg}: protected path: use uninstall or user delete")
            continue
        if not canAccess(target, session.getUsername(), session.getRole()):
            results.append(f"rm: {arg}: Permission denied")
            continue
        if not canDelete(target, session.getUsername()):
            results.append(f"rm: {arg}: Cannot delete protected path")
            continue
        if not target.exists():
            results.append(f"rm: {arg}: No such file or directory")
            continue
        try:
            if target.is_dir():
                shutil.rmtree(target)
            else:
                target.unlink()
        except Exception as e:
            results.append(f"rm: {arg}: {e}")
    return "\n".join(results)
def cmdCp(args: list, session) -> str:
    if len(args) < 2:
        return "cp: missing operand"
    src = resolvePath(session.getCurrentPath(), args[0])
    dst = resolvePath(session.getCurrentPath(), args[1])
    if not isInsideSandbox(src) or not isInsideSandbox(dst):
        return "cp: access denied"
    if not canManualCopy(src, dst):
        return "cp: protected path: operation blocked"
    if not canAccess(src, session.getUsername(), session.getRole()):
        return "cp: Permission denied"
    dstParent = dst if dst.exists() and dst.is_dir() else dst.parent
    if not canAccess(dstParent, session.getUsername(), session.getRole()):
        return "cp: Permission denied"
    if not src.exists():
        return f"cp: {args[0]}: No such file or directory"
    try:
        if src.is_dir():
            shutil.copytree(src, dst)
        else:
            shutil.copy2(src, dst)
    except Exception as e:
        return f"cp: {e}"
    return ""
def cmdMv(args: list, session) -> str:
    if len(args) < 2:
        return "mv: missing operand"
    src = resolvePath(session.getCurrentPath(), args[0])
    dst = resolvePath(session.getCurrentPath(), args[1])
    if not isInsideSandbox(src) or not isInsideSandbox(dst):
        return "mv: access denied"
    if not canManualMove(src, dst):
        return "mv: protected path: operation blocked"
    if not canAccess(src, session.getUsername(), session.getRole()):
        return "mv: Permission denied"
    dstParent = dst if dst.exists() and dst.is_dir() else dst.parent
    if not canAccess(dstParent, session.getUsername(), session.getRole()):
        return "mv: Permission denied"
    if not src.exists():
        return f"mv: {args[0]}: No such file or directory"
    if not canDelete(src, session.getUsername()):
        return f"mv: {args[0]}: Cannot move protected path"
    try:
        shutil.move(str(src), str(dst))
    except Exception as e:
        return f"mv: {e}"
    return ""
def cmdUser(args: list, session) -> str:
    if not args:
        return "user: missing action (create|delete|list|passwd)"
    action = args[0].lower()
    if action == "list":
        users = listUsers()
        if not users:
            return "No users found."
        return "\n".join(users)
    elif action == "create":
        if not session.isAdmin():
            return "user: Permission denied"
        if len(args) < 2:
            return "user create: missing username"
        username = args[1]
        if len(args) < 3:
            import getpass
            try:
                password = getpass.getpass(f"Password for {username}: ")
            except Exception:
                return "user create: cannot read password"
        else:
            password = args[2]
        role = args[3] if len(args) > 3 else "user"
        if role not in ("admin", "user"):
            return "user create: role must be 'admin' or 'user'"
        return createUser(username, password, role)
    elif action == "delete":
        if not session.isAdmin():
            return "user: Permission denied"
        if len(args) < 2:
            return "user delete: missing username"
        username = args[1]
        if username == ADMIN_USER:
            return "user delete: cannot delete built-in admin"
        if not userExists(username):
            return f"user delete: '{username}' not found"
        targetProfile = getProfile(username)
        targetRole = targetProfile.get("role", "user")
        if targetRole == "admin":
            import getpass
            try:
                confirmName = getpass.getpass(f"Type username to confirm deletion of admin '{username}': ")
            except Exception:
                return "user delete: cannot read confirmation"
            if confirmName != username:
                return "user delete: confirmation failed, aborted"
        else:
            import getpass
            try:
                confirmPassword = getpass.getpass(f"Password for {username}: ")
            except Exception:
                return "user delete: cannot read confirmation"
            if hashPassword(confirmPassword) != targetProfile.get("password"):
                return "user delete: wrong password, aborted"
        return deleteUser(username)
    elif action == "passwd":
        if len(args) < 2:
            return "user passwd: missing username"
        username = args[1]
        if username != session.getUsername() and not session.isAdmin():
            return "user passwd: Permission denied"
        import getpass
        try:
            newPass = getpass.getpass(f"New password for {username}: ")
        except Exception:
            return "user passwd: cannot read password"
        return changePassword(username, newPass)
    else:
        return f"user: unknown action '{action}' (create|delete|list|passwd)"
def cmdInstall(args: list, session) -> str:
    if not session.isAdmin():
        return "install: Permission denied (admin only)"
    if not args:
        return "install: missing .AppInstaller file"
    rawPath = args[0]
    if rawPath.startswith("/"):
        resolved = (VISTRO_ROOT / rawPath.lstrip("/")).resolve()
    else:
        resolved = resolvePath(session.getCurrentPath(), rawPath)
    if not isInsideSandbox(resolved):
        return "install: access denied: path outside sandbox"
    if not resolved.exists():
        return f"install: {rawPath}: file not found"
    if not resolved.suffix == ".AppInstaller" and not str(resolved).endswith(APP_INSTALLER_EXT):
        return f"install: {rawPath}: not a .AppInstaller file"
    try:
        with zipfile.ZipFile(resolved, "r") as zf:
            names = zf.namelist()
            if APP_COMMAND_FILE not in names:
                return f"install: invalid package: missing {APP_COMMAND_FILE}"
            if APP_MANIFEST_FILE not in names:
                return f"install: invalid package: missing {APP_MANIFEST_FILE}"
            manifestData = json.loads(zf.read(APP_MANIFEST_FILE).decode("utf-8"))
            rawName = str(manifestData.get("name", resolved.stem))
            appName = rawName.replace(" ", "")
            if not appName or "/" in appName or "\\" in appName or ".." in appName:
                return "install: invalid manifest name"
            installDir = VISTRO_PROGRAMS / appName
            dataDir = VISTRO_DATA / appName
            installDir.mkdir(parents=True, exist_ok=True)
            dataDir.mkdir(parents=True, exist_ok=True)
            for name in names:
                if not isSafeMemberName(name):
                    return f"install: unsafe member: {name}"
                targetFile = safeJoin(installDir, name)
                if targetFile is None:
                    return f"install: unsafe member: {name}"
                targetFile.parent.mkdir(parents=True, exist_ok=True)
                targetFile.write_bytes(zf.read(name))
        return f"Installed '{appName}' to programs/{appName}/"
    except zipfile.BadZipFile:
        return f"install: {rawPath}: not a valid zip/AppInstaller file"
    except Exception as e:
        return f"install: {e}"
def cmdUninstall(args: list, session) -> str:
    if not session.isAdmin():
        return "uninstall: Permission denied (admin only)"
    if not args:
        return "uninstall: missing program"
    programName = args[0]
    programDir = VISTRO_PROGRAMS / programName
    if not programDir.exists():
        programDir = VISTRO_PROGRAMS / programName.capitalize()
    if not programDir.exists() and VISTRO_PROGRAMS.exists():
        lowered = programName.lower()
        for entry in VISTRO_PROGRAMS.iterdir():
            if entry.is_dir() and entry.name.lower() == lowered:
                programDir = entry
                break
    if not programDir.exists():
        return f"uninstall: {programName}: program not found"
    session.setPendingUninstall(programDir.name)
    return f"uninstall: remove '{programDir.name}' and its data? [Y/N]"
def cmdSudo(args: list, session) -> str:
    if not session.isAdmin():
        return "sudo: Permission denied (admin only)"
    if not args:
        return "sudo: missing program"
    programName = args[0]
    programArgs = args[1:]
    programDir = VISTRO_PROGRAMS / programName
    if not programDir.exists():
        programDir = VISTRO_PROGRAMS / programName.capitalize()
    if not programDir.exists() and VISTRO_PROGRAMS.exists():
        lowered = programName.lower()
        for entry in VISTRO_PROGRAMS.iterdir():
            if entry.is_dir() and entry.name.lower() == lowered:
                programDir = entry
                break
    if not programDir.exists():
        return f"sudo: {programName}: program not found"
    cmdFile = programDir / APP_COMMAND_FILE
    if not cmdFile.exists():
        return f"sudo: {programName}: missing {APP_COMMAND_FILE}"
    try:
        content = cmdFile.read_text(encoding="utf-8")
    except Exception as e:
        return f"sudo: {e}"
    session.setPendingSudo(programDir.name, content, [programDir.name] + programArgs)
    return f"sudo: run '{programDir.name}' with elevated Vistro privileges? [Y/N]"
