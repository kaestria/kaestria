import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from fs.Sandbox import isInsideSandbox, canManualZip, safeJoin, isSafeMemberName
import zipfile
class ZipModule:
    @staticmethod
    def zipPath(zipTarget: Path, srcPath: Path) -> bool:
        try:
            if not isInsideSandbox(zipTarget) or not isInsideSandbox(srcPath):
                return False
            if not canManualZip(zipTarget) or not canManualZip(srcPath):
                return False
            if not srcPath.exists():
                return False
            zipTarget.parent.mkdir(parents=True, exist_ok=True)
            with zipfile.ZipFile(zipTarget, "w", zipfile.ZIP_DEFLATED) as zf:
                if srcPath.is_dir():
                    for item in sorted(srcPath.rglob("*")):
                        if item.is_file():
                            zf.write(item, item.relative_to(srcPath))
                else:
                    zf.write(srcPath, srcPath.name)
            return True
        except Exception:
            return False
    @staticmethod
    def unzipPath(zipSrc: Path, dstDir: Path) -> bool:
        try:
            if not isInsideSandbox(zipSrc) or not isInsideSandbox(dstDir):
                return False
            if not canManualZip(zipSrc) or not canManualZip(dstDir):
                return False
            if not zipSrc.exists():
                return False
            dstDir.mkdir(parents=True, exist_ok=True)
            with zipfile.ZipFile(zipSrc, "r") as zf:
                for name in zf.namelist():
                    if not isSafeMemberName(name):
                        return False
                    target = safeJoin(dstDir, name)
                    if target is None:
                        return False
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(zf.read(name))
            return True
        except Exception:
            return False
