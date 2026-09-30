# AppInstaller Packager

Creates `.AppInstaller` packages (zip with `command.AppCommand` + `manifest.json`).

## Pack

```bash
python bin/appcommand/Compiler.py apps/MyApp/MyApp.aplang apps/MyApp/command.AppCommand
python bin/appinstaller/Packager.py pack apps/MyApp dist/MyApp.AppInstaller
```

App dir layout expected:

```
apps/MyApp/
  manifest.json      # {"name":"MyApp", ...}
  command.AppCommand # compiled via Compiler.py
  <extra files...>   # included as-is
```

## Unpack (verify)

```bash
python bin/appinstaller/Packager.py unpack dist/MyApp.AppInstaller /tmp/myapp-test
```

## Install in Vistro

```
install MyApp.AppInstaller
MyApp help
sudo MyApp ...   # if elevated privileges needed
```
