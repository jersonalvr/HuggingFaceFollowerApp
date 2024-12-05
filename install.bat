@echo off
REM Crear entorno virtual y activarlo
python -m venv huggingface
huggingface\Scripts\activate

REM Instalar dependencias
pip install -r requirements.txt

REM Crear ejecutable con PyInstaller
pyinstaller --onefile --windowed --icon=hf-logo.ico --add-data "hf-logo.png;." --add-data "hf-logo.ico;." --add-binary "chromedriver.exe;." --noconsole huggingface.py

REM Ejecutar el archivo generado
dist\huggingface.exe
