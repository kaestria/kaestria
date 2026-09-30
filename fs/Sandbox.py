import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from kernel.system.Constant import VISTRO_ROOT, VISTRO_USERS, VISTRO_PROGRAMS, VISTRO_DATA, VISTRO_SHELL, PROFILE_FILE, ADMIN_USER
def resolvePath(currentPath: Path, target: str) -> Path:
    if target == "~" or target == "":
        return VISTRO_ROOT
    target = target.replace("~", str(VISTRO_ROOT))
    resolved = (currentPath / target).resolve()
    return resolved
def isInsideSandbox(path: Path) -> bool:
    try:
        path.resolve().relative_to(VISTRO_ROOT.resolve())
        return True
    except ValueError:
        return False
def getContainerRoot(path: Path):
    try:
        resolved = path.resolve()
    except Exception:
        return None
    for root in (VISTRO_USERS, VISTRO_PROGRAMS, VISTRO_DATA):
        try:
            resolved.relative_to(root.resolve())
            return root.resolve()
        except ValueError:
            pass
        try:
            if resolved == root.resolve():
                return root.resolve()
        except Exception:
            pass
    return None
def isContainerRoot(path: Path) -> bool:
    try:
        resolved = path.resolve()
    except Exception:
        return False
    for root in (VISTRO_USERS, VISTRO_PROGRAMS, VISTRO_DATA, VISTRO_SHELL, VISTRO_ROOT):
        try:
            if resolved == root.resolve():
                return True
        except Exception:
            pass
    return False
def isContainerChild(path: Path) -> bool:
    try:
        resolved = path.resolve()
    except Exception:
        return False
    for root in (VISTRO_USERS, VISTRO_PROGRAMS, VISTRO_DATA):
        try:
            parent = resolved.parent
            if parent == root.resolve():
                return True
        except Exception:
            pass
    return False
def isProtectedManualPath(path: Path) -> bool:
    return isContainerRoot(path) or isContainerChild(path)
def isSafeMemberName(name: str) -> bool:
    if not name:
        return False
    p = Path(name)
    if p.is_absolute():
        return False
    for part in p.parts:
        if part in ("..", "."):
            return False
    return True
def safeJoin(base: Path, name: str):
    if not isSafeMemberName(name):
        return None
    target = (base / name).resolve()
    try:
        target.relative_to(base.resolve())
        return target
    except ValueError:
        return None
def canDelete(path: Path, username: str) -> bool:
    resolved = path.resolve()
    sensitive = [
        VISTRO_USERS.resolve(),
        VISTRO_PROGRAMS.resolve(),
        VISTRO_DATA.resolve(),
        VISTRO_SHELL.resolve(),
        VISTRO_ROOT.resolve(),
    ]
    for s in sensitive:
        if resolved == s:
            return False
    if isContainerChild(path):
        return False
    if path.name == PROFILE_FILE:
        return False
    return True
def canAccess(path: Path, username: str, role: str) -> bool:
    if not isInsideSandbox(path):
        return False
    resolved = path.resolve()
    if role == "admin":
        return True
    usersDir = VISTRO_USERS.resolve()
    try:
        rel = resolved.relative_to(usersDir)
        parts = rel.parts
        if len(parts) > 0 and parts[0] != username:
            return False
    except ValueError:
        pass
    programsDir = VISTRO_PROGRAMS.resolve()
    dataDir = VISTRO_DATA.resolve()
    try:
        resolved.relative_to(programsDir)
        return False
    except ValueError:
        pass
    try:
        resolved.relative_to(dataDir)
        return False
    except ValueError:
        pass
    return True
def canModifyPrograms(username: str, role: str) -> bool:
    return role == "admin"
def canManualMkdir(path: Path) -> bool:
    if isProtectedManualPath(path):
        return False
    return True
def canManualRemove(path: Path) -> bool:
    if isProtectedManualPath(path):
        return False
    return True
def canManualCopy(src: Path, dst: Path) -> bool:
    if isProtectedManualPath(src) or isProtectedManualPath(dst):
        return False
    return True
def canManualMove(src: Path, dst: Path) -> bool:
    if isProtectedManualPath(src) or isProtectedManualPath(dst):
        return False
    return True
def canManualZip(path: Path) -> bool:
    if isProtectedManualPath(path):
        return False
    return True
