import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from kernel.system.Constant import APP_COMMAND_FILE, APP_MANIFEST_FILE, APP_INSTALLER_EXT
import json
import zipfile


def pack(app_dir: Path, output: Path | None = None) -> Path:
    app_dir = Path(app_dir)
    if not app_dir.is_dir():
        raise FileNotFoundError(f"App dir not found: {app_dir}")
    manifest_path = app_dir / APP_MANIFEST_FILE
    command_path = app_dir / APP_COMMAND_FILE
    if not manifest_path.exists():
        raise FileNotFoundError(f"Missing {APP_MANIFEST_FILE} in {app_dir}")
    if not command_path.exists():
        raise FileNotFoundError(
            f"Missing {APP_COMMAND_FILE} in {app_dir}. "
            f"Compile first: python bin/appcommand/Compiler.py <app.aplang> {APP_COMMAND_FILE}"
        )
    # Validate manifest
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    app_name = str(data.get("name", app_dir.name)).replace(" ", "")
    if not app_name:
        raise ValueError("Manifest 'name' is empty")
    if output is None:
        output = app_dir.parent / f"{app_name}{APP_INSTALLER_EXT}" if app_dir.name != app_name else app_dir / f"{app_name}{APP_INSTALLER_EXT}"
        # Prefer dist/ style: <app_dir>/<AppName>.AppInstaller if not specified
        # If app_dir is apps/DevTools, output = apps/DevTools/DevTools.AppInstaller
    else:
        output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in sorted(app_dir.rglob("*")):
            if f.is_file() and f.suffix != APP_INSTALLER_EXT and "__pycache__" not in f.parts:
                zf.write(f, f.relative_to(app_dir))
    return output


def unpack(installer: Path, dest_dir: Path) -> Path:
    installer = Path(installer)
    dest_dir = Path(dest_dir)
    if not installer.exists():
        raise FileNotFoundError(f"Installer not found: {installer}")
    with zipfile.ZipFile(installer, "r") as zf:
        names = zf.namelist()
        if APP_COMMAND_FILE not in names:
            raise ValueError(f"Invalid package: missing {APP_COMMAND_FILE}")
        if APP_MANIFEST_FILE not in names:
            raise ValueError(f"Invalid package: missing {APP_MANIFEST_FILE}")
        dest_dir.mkdir(parents=True, exist_ok=True)
        zf.extractall(dest_dir)
    return dest_dir


def run():
    if len(sys.argv) < 3:
        print(f"Usage:")
        print(f"  python Packager.py pack <appDir> [output{APP_INSTALLER_EXT}]")
        print(f"  python Packager.py unpack <package{APP_INSTALLER_EXT}> <destDir>")
        print(f"")
        print(f"Example:")
        print(f"  python bin/appcommand/Compiler.py apps/DevTools/DevTools.aplang apps/DevTools/command.AppCommand")
        print(f"  python bin/appinstaller/Packager.py pack apps/DevTools dist/DevTools.AppInstaller")
        sys.exit(1)
    action = sys.argv[1].lower()
    if action == "pack":
        app_dir = Path(sys.argv[2])
        out = Path(sys.argv[3]) if len(sys.argv) > 3 else None
        result = pack(app_dir, out)
        print(f"Packed: {result}")
    elif action == "unpack":
        if len(sys.argv) < 4:
            print(f"Usage: python Packager.py unpack <package{APP_INSTALLER_EXT}> <destDir>")
            sys.exit(1)
        result = unpack(Path(sys.argv[2]), Path(sys.argv[3]))
        print(f"Unpacked: {result}")
    else:
        print(f"Unknown action '{action}' (pack|unpack)")
        sys.exit(1)


if __name__ == "__main__":
    run()
