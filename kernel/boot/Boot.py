import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from kernel.system.Constant import VISTRO_HOME, VISTRO_ROOT, VISTRO_USERS, VISTRO_PROGRAMS, VISTRO_DATA, VISTRO_SHELL, HASH_ALGORITHM
import hashlib
import secrets
def hashPassword(password: str) -> str:
    return hashlib.new(HASH_ALGORITHM, password.encode()).hexdigest()
def createDirStructure():
    VISTRO_HOME.mkdir(parents=True, exist_ok=True)
    VISTRO_ROOT.mkdir(parents=True, exist_ok=True)
    VISTRO_USERS.mkdir(parents=True, exist_ok=True)
    VISTRO_PROGRAMS.mkdir(parents=True, exist_ok=True)
    VISTRO_DATA.mkdir(parents=True, exist_ok=True)
    VISTRO_SHELL.mkdir(parents=True, exist_ok=True)
def run():
    createDirStructure()
