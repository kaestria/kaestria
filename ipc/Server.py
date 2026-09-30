import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from kernel.system.Constant import API_HOST, API_PORT, PROFILE_FILE
from kernel.user.UserManager import getProfile
from ipc.login.LoginService import hashPassword, validateToken, createToken
from ipc.fs.FileService import resolveSandboxPath, isSensitivePath, canUserAccess
from fs.Sandbox import isSafeMemberName, safeJoin, isProtectedManualPath
import json
import zipfile
import shutil
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
def jsonResponse(handler, code: int, data: dict):
    body = json.dumps(data).encode("utf-8")
    handler.send_response(code)
    handler.send_header("Content-Type", "application/json")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)
def getAuthUser(handler) -> dict | None:
    auth = handler.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        token = auth[7:]
        return validateToken(token)
    return None
class VistroHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass
    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length)) if length > 0 else {}
        if path == "/api/login":
            username = body.get("username", "")
            password = body.get("password", "")
            if username == "admin":
                return jsonResponse(self, 403, {"error": "Admin login is konsole only", "success": False})
            hashed = hashPassword(password)
            profile = getProfile(username)
            if not profile or profile.get("password") != hashed:
                return jsonResponse(self, 401, {"error": "Invalid credentials", "success": False})
            token = createToken(username, profile.get("role", "user"))
            return jsonResponse(self, 200, {"token": token})
        user = getAuthUser(self)
        if not user:
            return jsonResponse(self, 401, {"error": "Unauthorized", "success": False})
        if path == "/api/mkdir":
            relPath = body.get("path", "")
            target = resolveSandboxPath(relPath)
            if not target:
                return jsonResponse(self, 403, {"error": "Access denied", "success": False})
            if not canUserAccess(target, user["username"], user["role"]):
                return jsonResponse(self, 403, {"error": "Access denied", "success": False})
            target.mkdir(parents=True, exist_ok=True)
            return jsonResponse(self, 200, {"success": True})
        elif path == "/api/file/create":
            relPath = body.get("path", "")
            content = body.get("content", "")
            target = resolveSandboxPath(relPath)
            if not target:
                return jsonResponse(self, 403, {"error": "Access denied", "success": False})
            if not canUserAccess(target, user["username"], user["role"]):
                return jsonResponse(self, 403, {"error": "Access denied", "success": False})
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
            return jsonResponse(self, 200, {"success": True})
        elif path == "/api/file/zip":
            source = body.get("source", "")
            output = body.get("output", "")
            srcPath = resolveSandboxPath(source)
            outPath = resolveSandboxPath(output)
            if not srcPath or not outPath:
                return jsonResponse(self, 403, {"error": "Access denied", "success": False})
            if not canUserAccess(srcPath, user["username"], user["role"]):
                return jsonResponse(self, 403, {"error": "Access denied", "success": False})
            if not canUserAccess(outPath.parent, user["username"], user["role"]):
                return jsonResponse(self, 403, {"error": "Access denied", "success": False})
            if isProtectedManualPath(srcPath) or isProtectedManualPath(outPath):
                return jsonResponse(self, 403, {"error": "Protected path", "success": False})
            if not srcPath.exists():
                return jsonResponse(self, 404, {"error": "Source not found", "success": False})
            outPath.parent.mkdir(parents=True, exist_ok=True)
            with zipfile.ZipFile(outPath, "w", zipfile.ZIP_DEFLATED) as zf:
                if srcPath.is_dir():
                    for f in srcPath.rglob("*"):
                        if f.is_file():
                            zf.write(f, f.relative_to(srcPath))
                else:
                    zf.write(srcPath, srcPath.name)
            return jsonResponse(self, 200, {"success": True})
        elif path == "/api/file/unzip":
            source = body.get("source", "")
            output = body.get("output", "")
            srcPath = resolveSandboxPath(source)
            outPath = resolveSandboxPath(output)
            if not srcPath or not outPath:
                return jsonResponse(self, 403, {"error": "Access denied", "success": False})
            if not canUserAccess(srcPath, user["username"], user["role"]):
                return jsonResponse(self, 403, {"error": "Access denied", "success": False})
            if not canUserAccess(outPath, user["username"], user["role"]):
                return jsonResponse(self, 403, {"error": "Access denied", "success": False})
            if isProtectedManualPath(srcPath) or isProtectedManualPath(outPath):
                return jsonResponse(self, 403, {"error": "Protected path", "success": False})
            if not srcPath.exists():
                return jsonResponse(self, 404, {"error": "Source not found", "success": False})
            outPath.mkdir(parents=True, exist_ok=True)
            with zipfile.ZipFile(srcPath, "r") as zf:
                for member in zf.namelist():
                    if not isSafeMemberName(member):
                        return jsonResponse(self, 400, {"error": "Unsafe member", "success": False})
                    target = safeJoin(outPath, member)
                    if target is None:
                        return jsonResponse(self, 400, {"error": "Unsafe member", "success": False})
                    if isProtectedManualPath(target):
                        return jsonResponse(self, 403, {"error": "Protected path", "success": False})
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(zf.read(member))
            return jsonResponse(self, 200, {"success": True})
        else:
            return jsonResponse(self, 404, {"error": "Not found", "success": False})
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        params = parse_qs(parsed.query)
        user = getAuthUser(self)
        if not user:
            return jsonResponse(self, 401, {"error": "Unauthorized", "success": False})
        if path == "/api/list":
            relPath = params.get("path", [""])[0]
            target = resolveSandboxPath(relPath)
            if not target:
                return jsonResponse(self, 403, {"error": "Access denied", "success": False})
            if not canUserAccess(target, user["username"], user["role"]):
                return jsonResponse(self, 403, {"error": "Access denied", "success": False})
            if not target.exists():
                return jsonResponse(self, 404, {"error": "Path not found", "success": False})
            files = []
            folders = []
            for entry in sorted(target.iterdir()):
                if entry.is_dir():
                    folders.append(entry.name)
                else:
                    files.append(entry.name)
            return jsonResponse(self, 200, {"files": files, "folders": folders})
        elif path == "/api/file/read":
            relPath = params.get("path", [""])[0]
            target = resolveSandboxPath(relPath)
            if not target:
                return jsonResponse(self, 403, {"error": "Access denied", "success": False})
            if not canUserAccess(target, user["username"], user["role"]):
                return jsonResponse(self, 403, {"error": "Access denied", "success": False})
            if not target.exists():
                return jsonResponse(self, 404, {"error": "File not found", "success": False})
            content = target.read_text(encoding="utf-8")
            return jsonResponse(self, 200, {"content": content})
        else:
            return jsonResponse(self, 404, {"error": "Not found", "success": False})
    def do_PUT(self):
        parsed = urlparse(self.path)
        path = parsed.path
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length)) if length > 0 else {}
        user = getAuthUser(self)
        if not user:
            return jsonResponse(self, 401, {"error": "Unauthorized", "success": False})
        if path == "/api/file/replace":
            relPath = body.get("path", "")
            content = body.get("content", "")
            target = resolveSandboxPath(relPath)
            if not target:
                return jsonResponse(self, 403, {"error": "Access denied", "success": False})
            if not canUserAccess(target, user["username"], user["role"]):
                return jsonResponse(self, 403, {"error": "Access denied", "success": False})
            if not target.exists():
                return jsonResponse(self, 404, {"error": "File not found", "success": False})
            target.write_text(content, encoding="utf-8")
            return jsonResponse(self, 200, {"success": True})
        elif path == "/api/file/edit":
            relPath = body.get("path", "")
            old = body.get("old", "")
            new = body.get("new", "")
            target = resolveSandboxPath(relPath)
            if not target:
                return jsonResponse(self, 403, {"error": "Access denied", "success": False})
            if not canUserAccess(target, user["username"], user["role"]):
                return jsonResponse(self, 403, {"error": "Access denied", "success": False})
            if not target.exists():
                return jsonResponse(self, 404, {"error": "File not found", "success": False})
            content = target.read_text(encoding="utf-8")
            if old not in content:
                return jsonResponse(self, 400, {"error": "Text not found", "success": False})
            target.write_text(content.replace(old, new, 1), encoding="utf-8")
            return jsonResponse(self, 200, {"success": True})
        else:
            return jsonResponse(self, 404, {"error": "Not found", "success": False})
    def do_DELETE(self):
        parsed = urlparse(self.path)
        path = parsed.path
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length)) if length > 0 else {}
        user = getAuthUser(self)
        if not user:
            return jsonResponse(self, 401, {"error": "Unauthorized", "success": False})
        if path == "/api/file/delete":
            relPath = body.get("path", "")
            target = resolveSandboxPath(relPath)
            if not target:
                return jsonResponse(self, 403, {"error": "Access denied", "success": False})
            if not canUserAccess(target, user["username"], user["role"]):
                return jsonResponse(self, 403, {"error": "Access denied", "success": False})
            if isSensitivePath(target):
                return jsonResponse(self, 403, {"error": "Cannot delete protected path", "success": False})
            if target.name == PROFILE_FILE:
                return jsonResponse(self, 403, {"error": "Cannot delete profile.json", "success": False})
            if not target.exists():
                return jsonResponse(self, 404, {"error": "Not found", "success": False})
            if target.is_dir():
                shutil.rmtree(target)
            else:
                target.unlink()
            return jsonResponse(self, 200, {"success": True})
        else:
            return jsonResponse(self, 404, {"error": "Not found", "success": False})
def run():
    server = HTTPServer((API_HOST, API_PORT), VistroHandler)
    server.serve_forever()
