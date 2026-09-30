import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from kernel.system.Constant import SHELL_MANIFEST, SHELL_BIN, SHELL_MAIN, SHELL_EXT
from bin.shell.Language import ShellCompiler
import json
import zipfile
import io
def buildShell(sourceDir: Path, outputPath: Path) -> Path:
    sourceDir = Path(sourceDir)
    outputPath = Path(outputPath)
    manifestPath = sourceDir / SHELL_MANIFEST
    mainPath = sourceDir / SHELL_MAIN
    if not manifestPath.exists():
        raise FileNotFoundError("missing manifest.json")
    if not mainPath.exists() or not mainPath.is_file():
        raise FileNotFoundError("missing Main")
    manifest = json.loads(manifestPath.read_text(encoding="utf-8"))
    innerBuffer = io.BytesIO()
    with zipfile.ZipFile(innerBuffer, "w", zipfile.ZIP_DEFLATED) as inner:
        for entry in sorted(sourceDir.rglob("*")):
            if not entry.is_file():
                continue
            if entry.name == SHELL_MANIFEST:
                continue
            if entry.suffix == SHELL_EXT:
                continue
            rel = entry.relative_to(sourceDir).as_posix()
            if "." not in entry.name:
                source = entry.read_text(encoding="utf-8")
                compiler = ShellCompiler()
                bytecode = compiler.compile(source)
                inner.writestr(rel, compiler.toHexFile(bytecode))
            else:
                inner.writestr(rel, entry.read_bytes())
    outputPath.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(outputPath, "w", zipfile.ZIP_DEFLATED) as outer:
        outer.writestr(SHELL_MANIFEST, json.dumps(manifest, indent=2))
        outer.writestr(SHELL_BIN, innerBuffer.getvalue())
    return outputPath
def run():
    if len(sys.argv) < 3:
        print("Usage:")
        print("  python Compiler.py <sourceDir> <output.shell>")
        sys.exit(1)
    result = buildShell(Path(sys.argv[1]), Path(sys.argv[2]))
    print(f"Built: {result}")
if __name__ == "__main__":
    run()
