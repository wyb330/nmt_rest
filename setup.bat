@echo off

REM Python�� �̹� ��ġ�Ǿ� �ִ��� Ȯ��
python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo Python is already installed.
) else (
    echo Python is not installed, start installation...
    
    REM Python ��ġ ���� �ٿ�ε�
    echo Download Python installation file...
    curl -L -o python_installer.exe https://www.python.org/ftp/python/3.11.5/python-3.11.5-amd64.exe
    
    REM Python ��ġ (�⺻ ��ο� ��ġ, PATH�� �߰�)
    echo Install Python...
    start /wait python_installer.exe /quiet InstallAllUsers=1 PrependPath=1 Include_pip=1
    
    REM ��ġ ���� ����
    del python_installer.exe
    
    echo Python installation is complete.
)

REM UV ��ġ
echo Install UV...
curl -L -o install-uv.ps1 https://astral.sh/uv/install.ps1
powershell -ExecutionPolicy Bypass -File install-uv.ps1
del install-uv.ps1

REM UV PATH ���� (�Ϲ������� %USERPROFILE%\.cargo\bin ��ο� ��ġ��)
set PATH=%PATH%;%USERPROFILE%\.cargo\bin
echo UV UV installation is complete.

REM UV�� �̿��� ����ȯ�� ����
echo UCreate Python virtual environments with UV...
uv venv .venv

REM �ʿ��� ���̺귯�� ��ġ
echo Install the required library...

uv pip install torch==2.5.1

REM requirements.txt ������ �����ϴ��� Ȯ��
if exist requirements.txt (
    uv pip install -r requirements.txt
    echo Library installation has been completed.
) 

echo Download model...
mkdir models
uv run download.py "Darong/BlueT" --save_dir models

REM ���� ���� ����
echo ====================================
echo Create a program executable...

REM run.bat ���� ���� (���α׷� �����)
echo @echo off > run.bat
echo uv run server.py  >> run.bat
echo pause >> run.bat

echo Double-click the run.bat file that was created to run the program.
echo ====================================

pause
