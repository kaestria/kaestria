import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from kernel.user.UserManager import getProfile, hashPassword
import secrets
_tokens = {}
def loginUser(username: str, password: str, shellName: str):
    try:
        profile = getProfile(str(username or ""))
        if not profile:
            return -1
        if profile.get("password") != hashPassword(str(password or "")):
            return -1
        token = secrets.token_hex(16)
        _tokens[token] = {
            "username": str(username),
            "role": profile.get("role", "user"),
            "shell": str(shellName or "")
        }
        return token
    except Exception:
        return -1
def logoutToken(token: str) -> bool:
    try:
        if str(token or "") in _tokens:
            del _tokens[str(token or "")]
            return True
        return False
    except Exception:
        return False
def validateToken(token: str):
    try:
        return _tokens.get(str(token or ""))
    except Exception:
        return None
def clearShellTokens(shellName: str):
    try:
        doomed = [k for k, v in _tokens.items() if v.get("shell") == str(shellName or "")]
        for k in doomed:
            del _tokens[k]
    except Exception:
        pass
def tokenUser(token: str):
    data = validateToken(token)
    if not data:
        return None
    return data.get("username")
def tokenRole(token: str):
    data = validateToken(token)
    if not data:
        return None
    return data.get("role", "user")
