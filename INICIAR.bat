@echo off
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe (
  py -3.12 -m venv .venv
  if errorlevel 1 goto error
)
.venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 goto error
.venv\Scripts\python.exe manage.py migrate
if errorlevel 1 goto error
.venv\Scripts\python.exe manage.py demo
if errorlevel 1 goto error
start "" http://127.0.0.1:8000
.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
goto end
:error
echo No se pudo iniciar. Revisa el error anterior y las instrucciones del README.
pause
:end
