@echo off

set "CUDA_VERSION=12.4.0"
set "DOWNLOAD_DIR=%USERPROFILE%\Downloads\CUDA_Installer"
set "CUDA_INSTALLER=cuda_12.4.0_551.61_windows.exe"
set "CUDA_URL=https://developer.download.nvidia.com/compute/cuda/%CUDA_VERSION%/local_installers/%CUDA_INSTALLER%"
set "CUDA_PATH=C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.4"

:: Create download directory
if not exist "%DOWNLOAD_DIR%" (
    echo Creating download directory: %DOWNLOAD_DIR%
    mkdir "%DOWNLOAD_DIR%"
)

:: Download CUDA Toolkit
echo Downloading CUDA Toolkit %CUDA_VERSION%...
echo Downloading may take more than a few minutes...
if not exist "%DOWNLOAD_DIR%\%CUDA_INSTALLER%" (
    powershell -Command "& {$ProgressPreference = 'SilentlyContinue'; Invoke-WebRequest -Uri '%CUDA_URL%' -OutFile '%DOWNLOAD_DIR%\%CUDA_INSTALLER%'}"
    if %ERRORLEVEL% neq 0 (
        echo Failed to download CUDA Toolkit. Please check your internet connection or download manually from:
        echo https://developer.nvidia.com/cuda-downloads
        exit /b 1
    )
) else (
    echo CUDA Toolkit installer already downloaded.
)

:: Install CUDA Toolkit
echo Installing CUDA Toolkit %CUDA_VERSION%...
echo This may take several minutes. Please be patient.
"%DOWNLOAD_DIR%\%CUDA_INSTALLER%" /s
if %ERRORLEVEL% neq 0 (
    echo Failed to install CUDA Toolkit. Please try installing manually.
    exit /b 1
)

:: Verify CUDA installation
echo Verifying CUDA installation...
if exist "%CUDA_PATH%\bin\cudart64_*.dll" (
    echo CUDA Toolkit installation verified.
) else (
    echo CUDA Toolkit installation could not be verified at %CUDA_PATH%.
)

:: Add CUDA to PATH
echo Adding CUDA to system PATH...
setx PATH "%PATH%;%CUDA_PATH%\bin" /M


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
echo UV installation is complete.

REM UV를 이용한 가상환경 생성
echo Create Python virtual environments with UV...
uv venv .venv

REM 필요한 라이브러리 설치
echo Install the required library...

uv pip install torch==2.5.1 --index-url https://download.pytorch.org/whl/cu124

REM requirements.txt 파일이 존재하는지 확인
if exist requirements.txt (
    uv pip install -r requirements.txt
    echo Library installation has been completed.
) 

echo Download model...
echo uv run download.py "Darong/BlueT" --save_dir models

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
