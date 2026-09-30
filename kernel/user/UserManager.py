import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from kernel.system.Constant import VISTRO_USERS, PROFILE_FILE, HASH_ALGORITHM
import json
import hashlib
def hashPassword(password: str) -> str:
    return hashlib.new(HASH_ALGORITHM, password.encode()).hexdigest()
def userExists(username: str) -> bool:
    return (VISTRO_USERS / username / PROFILE_FILE).exists()
def createUser(username: str, password: str, role: str) -> str:
    if userExists(username):
        return f"User '{username}' already exists."
    userDir = VISTRO_USERS / username
    userDir.mkdir(parents=True, exist_ok=True)
    profile = {
        "username": username,
        "password": hashPassword(password),
        "role": role,
        "home": str(userDir)
    }
    (userDir / PROFILE_FILE).write_text(json.dumps(profile, indent=4))
    return f"User '{username}' created with role '{role}'."
def deleteUser(username: str) -> str:
    if not userExists(username):
        return f"User '{username}' not found."
    import shutil
    shutil.rmtree(VISTRO_USERS / username)
    return f"User '{username}' deleted."
def listUsers() -> list:
    if not VISTRO_USERS.exists():
        return []
    return [d.name for d in VISTRO_USERS.iterdir() if d.is_dir()]
def getProfile(username: str) -> dict:
    profilePath = VISTRO_USERS / username / PROFILE_FILE
    if not profilePath.exists():
        return {}
    return json.loads(profilePath.read_text())
def changePassword(username: str, newPassword: str) -> str:
    if not userExists(username):
        return f"User '{username}' not found."
    profilePath = VISTRO_USERS / username / PROFILE_FILE
    profile = json.loads(profilePath.read_text())
    profile["password"] = hashPassword(newPassword)
    profilePath.write_text(json.dumps(profile, indent=4))
    return f"Password changed for '{username}'."
