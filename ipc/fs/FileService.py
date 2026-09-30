import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from kernel.system.Constant import VISTRO_ROOT, VISTRO_USERS, VISTRO_PROGRAMS, VISTRO_DATA, VISTRO_SHELL
def resolveSandboxPath(relPath: str) -> Path | None:
    relPath = relPath.lstrip("/")
    resolved = (VISTRO_ROOT / relPath).resolve()
    try:
        resolved.relative_to(VISTRO_ROOT.resolve())
        return resolved
    except ValueError:
        return None
def isSensitivePath(path: Path) -> bool:
    try:
        resolved = path.resolve()
    except Exception:
        return True
    for base in (VISTRO_USERS, VISTRO_PROGRAMS, VISTRO_DATA, VISTRO_SHELL, VISTRO_ROOT):
        try:
            if resolved == base.resolve():
                return True
        except Exception:
            pass
    for base in (VISTRO_USERS, VISTRO_PROGRAMS, VISTRO_DATA):
        try:
            if resolved.parent == base.resolve():
                return True
        except Exception:
            pass
    return False
def canUserAccess(path: Path, username: str, role: str) -> bool:
    if role == "admin":
        return True
    resolved = path.resolve()
    usersDir = VISTRO_USERS.resolve()
    try:
        rel = resolved.relative_to(usersDir)
        parts = rel.parts
        if len(parts) > 0 and parts[0] != username:
            return False
    except ValueError:
        try:
            resolved.relative_to(VISTRO_PROGRAMS.resolve())
            return False
        except ValueError:
            pass
        try:
            resolved.relative_to(VISTRO_DATA.resolve())
            return False
        except ValueError:
            pass
    return True
