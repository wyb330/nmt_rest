@echo off

REM Python이 이미 설치되어 있는지 확인
python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo Python is already installed.
) else (
    echo Python is not installed, start installation...
    
    REM Python 설치 파일 다운로드
    echo Download Python installation file...
    curl -L -o python_installer.exe https://www.python.org/ftp/python/3.11.5/python-3.11.5-amd64.exe
    
    REM Python 설치 (기본 경로에 설치, PATH에 추가)
    echo Install Python...
    start /wait python_installer.exe /quiet InstallAllUsers=1 PrependPath=1 Include_pip=1
    
    REM 설치 파일 삭제
    del python_installer.exe
    
    echo Python installation is complete.
)

REM UV 설치
echo Install UV...
curl -L -o install-uv.ps1 https://astral.sh/uv/install.ps1
powershell -ExecutionPolicy Bypass -File install-uv.ps1
del install-uv.ps1

REM UV PATH 설정 (일반적으로 %USERPROFILE%\.cargo\bin 경로에 설치됨)
set PATH=%PATH%;%USERPROFILE%\.cargo\bin
echo UV UV installation is complete.

REM UV를 이용한 가상환경 생성
echo UCreate Python virtual environments with UV...
uv venv .venv

REM 필요한 라이브러리 설치
echo Install the required library...

uv pip install torch==2.5.1

REM requirements.txt 파일이 존재하는지 확인
if exist requirements.txt (
    uv pip install -r requirements.txt
    echo Library installation has been completed.
) 

echo Download model...
mkdir models
uv run download.py "Darong/BlueT" --save_dir models

REM 실행 파일 생성
echo ====================================
echo Create a program executable...

REM run.bat 파일 생성 (프로그램 실행용)
echo @echo off > run.bat
echo uv run server.py  >> run.bat
echo pause >> run.bat

echo Double-click the run.bat file that was created to run the program.
echo ====================================

pause
