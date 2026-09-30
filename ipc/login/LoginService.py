import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from kernel.system.Constant import VISTRO_ROOT, ADMIN_USER, PROFILE_FILE, TOKEN_LENGTH, TOKEN_EXPIRY_SECONDS, HASH_ALGORITHM
from kernel.user.UserManager import getProfile
import json
import secrets
import hashlib
import time
_tokens = {}
def hashPassword(password: str) -> str:
    return hashlib.new(HASH_ALGORITHM, password.encode()).hexdigest()
def generateToken() -> str:
    return secrets.token_hex(TOKEN_LENGTH)
def createToken(username: str, role: str) -> str:
    token = generateToken()
    _tokens[token] = {
        "username": username,
        "role": role,
        "expires": time.time() + TOKEN_EXPIRY_SECONDS
    }
    return token
def validateToken(token: str) -> dict | None:
    if token not in _tokens:
        return None
    data = _tokens[token]
    if time.time() > data["expires"]:
        del _tokens[token]
        return None
    return data
def getAdminProfile() -> dict:
    adminFile = VISTRO_ROOT.parent / PROFILE_FILE
    if adminFile.exists():
        return json.loads(adminFile.read_text())
    return {"username": ADMIN_USER, "password": hashPassword("admin"), "role": "admin"}
def loginUser(username: str, password: str) -> dict:
    if username == ADMIN_USER:
        return {"success": False, "error": "Admin login is konsole only"}
    hashed = hashPassword(password)
    profile = getProfile(username)
    if not profile or profile.get("password") != hashed:
        return {"success": False, "error": "Invalid credentials"}
    token = createToken(username, profile.get("role", "user"))
    return {"success": True, "token": token}
