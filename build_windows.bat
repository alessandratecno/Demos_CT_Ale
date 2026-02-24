@echo off
setlocal

if not exist .venv (
  py -m venv .venv
)

call .venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-build.txt

pyinstaller --noconfirm --clean --onefile --name NotaSeguraApp --add-data "templates;templates" --add-data "static;static" app.py

echo.
echo Build finalizado. Arquivo gerado em: dist\NotaSeguraApp.exe
endlocal
