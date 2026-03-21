@echo off
setlocal

set "port=%~1"
if "%port%"=="" (
    set "port=5000"
    echo No port specified. Using default port %port%.
)

set "FLASK_APP=app.py"
flask --app app run --host 0.0.0.0 -p %port%
