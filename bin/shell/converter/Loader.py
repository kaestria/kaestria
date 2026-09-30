import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from kernel.system.Constant import VISTRO_SHELL, SHELL_EXT, SHELL_MANIFEST, SHELL_BIN, SHELL_MAIN
from fs.Sandbox import isSafeMemberName, safeJoin
from bin.shell.Language import fromHexFile
import json
import zipfile
import io
def listShells() -> list:
    try:
        VISTRO_SHELL.mkdir(parents=True, exist_ok=True)
    except Exception:
        return []
    result = []
    try:
        for entry in VISTRO_SHELL.iterdir():
            if entry.is_file() and entry.name.endswith(SHELL_EXT):
                result.append(entry.stem)
    except Exception:
        pass
    seen = set()
    unique = []
    for stem in sorted(result):
        lowered = stem.lower()
        if lowered not in seen:
            seen.add(lowered)
            unique.append(stem)
    return unique
def findShellFile(name: str):
    try:
        base = str(name or "").strip()
        if not base:
            return None
        if base.endswith(SHELL_EXT):
            stem = base[: -len(SHELL_EXT)]
        else:
            stem = base
        if "/" in stem or "\\" in stem or ".." in stem:
            return None
        candidate = VISTRO_SHELL / f"{stem}{SHELL_EXT}"
        if candidate.exists() and candidate.is_file():
            return candidate
        if VISTRO_SHELL.exists():
            lowered = stem.lower()
            for entry in VISTRO_SHELL.iterdir():
                if entry.is_file() and entry.name.endswith(SHELL_EXT) and entry.stem.lower() == lowered:
                    return entry
    except Exception:
        pass
    return None
def loadShell(name: str) -> dict:
    path = findShellFile(name)
    if path is None:
        return {"success": False, "error": f"shell not found: {name}"}
    try:
        (VISTRO_SHELL / path.stem).mkdir(parents=True, exist_ok=True)
    except Exception:
        pass
    try:
        with zipfile.ZipFile(path, "r") as outer:
            names = outer.namelist()
            if SHELL_MANIFEST not in names:
                return {"success": False, "error": "invalid shell: missing manifest.json"}
            if SHELL_BIN not in names:
                return {"success": False, "error": "invalid shell: missing bin"}
            manifest = json.loads(outer.read(SHELL_MANIFEST).decode("utf-8"))
            innerBytes = outer.read(SHELL_BIN)
    except zipfile.BadZipFile:
        return {"success": False, "error": "invalid shell package"}
    except Exception as e:
        return {"success": False, "error": str(e)}
    try:
        modules = {}
        assets = {}
        mainHex = None
        with zipfile.ZipFile(io.BytesIO(innerBytes), "r") as inner:
            for member in inner.namelist():
                if not isSafeMemberName(member):
                    return {"success": False, "error": f"unsafe member: {member}"}
                raw = inner.read(member)
                if "." not in Path(member).name:
                    try:
                        text = raw.decode("utf-8")
                        bytecode = fromHexFile(text)
                        if member == SHELL_MAIN:
                            mainHex = text
                            modules[SHELL_MAIN] = bytecode
                        else:
                            key = member.replace("/", ".")
                            modules[key] = bytecode
                    except Exception:
                        assets[member] = raw
                else:
                    assets[member] = raw
        if mainHex is None:
            return {"success": False, "error": "invalid shell: missing Main"}
        return {"success": True, "manifest": manifest, "mainHex": mainHex, "modules": modules, "assets": assets, "path": path}
    except zipfile.BadZipFile:
        return {"success": False, "error": "invalid shell bin"}
    except Exception as e:
        return {"success": False, "error": str(e)}
def executeShell(name: str, args: list = None, vistroRoot=None, username: str = None, role: str = None) -> dict:
    from bin.shell.Interpreter import ShellInterpreter
    loaded = loadShell(name)
    if not loaded.get("success"):
        return loaded
    try:
        modules = loaded.get("modules", {})
        mainBytecode = modules.get(SHELL_MAIN)
        interp = ShellInterpreter(str(name), modules=modules, vistroRoot=vistroRoot, username=username, role=role)
        output = interp.execute(mainBytecode, args or [])
        return {"success": True, "output": output, "manifest": loaded.get("manifest")}
    except Exception as e:
        return {"success": False, "error": str(e)}
