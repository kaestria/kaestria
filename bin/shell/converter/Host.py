import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from bin.shell.converter.Loader import loadShell
from bin.shell.Interpreter import ShellInterpreter
from bin.shell.qml.Render import buildQml
import tempfile
def runShellHost(shellName: str, args: list) -> int:
    loaded = loadShell(shellName)
    if not loaded.get("success"):
        print(f"shell: {loaded.get('error')}")
        return 1
    display = Path(str(loaded.get("path", shellName))).stem
    modules = loaded.get("modules", {})
    assets = loaded.get("assets", {})
    workdir = Path(tempfile.mkdtemp(prefix=f"vistro-shell-{display}-"))
    for name, raw in assets.items():
        target = workdir / Path(name).name
        target.write_bytes(raw)
    interp = ShellInterpreter(display, modules=modules)
    output = interp.execute(modules.get("Main"), [display] + list(args or []))
    if output and output.strip():
        print(output.rstrip("\n"))
    for elem in interp.elements.values():
        if str(elem.get("type", "")) == "image":
            src = str(elem.get("props", {}).get("src", ""))
            if src and not src.startswith("file:") and not src.startswith("http"):
                candidate = workdir / Path(src).name
                if candidate.exists():
                    elem["props"]["src"] = candidate.as_uri()
    qml = buildQml(display, interp.windows, interp.elements)
    qmlPath = workdir / "Shell.qml"
    qmlPath.write_text(qml, encoding="utf-8")
    from PySide6.QtGui import QGuiApplication
    from PySide6.QtQml import QQmlApplicationEngine
    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()
    engine.load(str(qmlPath))
    if not engine.rootObjects():
        print("shell: failed to load interface")
        return 1
    return app.exec()
def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: Host.py <ShellName> [args]")
        return 1
    return runShellHost(sys.argv[1], sys.argv[2:])
if __name__ == "__main__":
    sys.exit(main())
