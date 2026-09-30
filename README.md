# VISTRO

Vistro is a Sandbox running on Windows/Linux. No setup needed.

## Run

```
python Core.py
```

## Compile .aplang to .AppCommand

```
python bin/appcommand/Compiler.py myapp.aplang myapp.AppCommand
```

## AppLang source syntax

```
ARGS args
ARGLEN argc
PRINTLN "Hello from Vistro"
INT x 10
ADD x x 5
PRINTLN x
```

## API

Runs on `http://127.0.0.1:7070`. Login: POST /api/login with `{"username":"admin","password":"admin"}`.

