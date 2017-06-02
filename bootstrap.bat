@REM This is mostly for windows 7. Recommend to run bootstrap.ps1 in Windows 10 instead.
@REM Author: Walter Chen
@REM Version: 0.1.1
@REM 0.1.0 - Successfully running in virtual machines, appveyor, and real machines.
@REM 0.1.1 - Adding instruction and changed the command for detecting admin privileges.
@REM 0.1.2 - Backing up the PATH variable for you in path.txt before running bootstrap

::::::::::::::::::::::::::::::::::::::::::::::::::::::
::                 *Instructions*                   ::
:: 1. download windows version of git               ::
:: 2. git clone the Hasle project                  ::
:: 3. run bootstrap                                 ::
:: 4. reopen command prompt and activate hasal-env  ::
::::::::::::::::::::::::::::::::::::::::::::::::::::::

@REM Assuming that you already git pull all the files, we can use curl from the repository
@REM Print out the time we started this script.

@echo off
for /F "usebackq tokens=1,2 delims==" %%i in (`wmic os get LocalDateTime /VALUE 2^>NUL`) do if '.%%i.'=='.LocalDateTime.' set ldt=%%j
set timestamp=%ldt:~0,4%%ldt:~4,2%%ldt:~6,2%%ldt:~8,2%%ldt:~10,2%
set ldt=%ldt:~0,4%-%ldt:~4,2%-%ldt:~6,2% %ldt:~8,2%:%ldt:~10,2%:%ldt:~12,6%
echo [INFO] Current date and time [%ldt%]

@IF EXIST bootstrap_backup_env_path_%timestamp%.txt (
    echo [INFO] bootstrap_backup_env_path_%timestamp%.txt exists. We will not replace it.
) ELSE (
    echo "%PATH%" > bootstrap_backup_env_path_%timestamp%.txt
    echo [INFO] your current PATH variable was backed up in bootstrap_backup_env_path_%timestamp%.txt
)

for /f "tokens=4-5 delims=. " %%i in ('ver') do set VERSION=%%i.%%j

IF NOT "%APPVEYOR%"=="True" (
    IF /I %version% GTR 6.2 (
        powershell .\bootstrap.ps1
    ) 
    IF /I %version% GTR 6.2 (
        EXIT /B 0
    )
)

::::::::::::::::::::
::  Prerequisite  ::
::::::::::::::::::::

SET PATH=%MINICONDA%;%MINICONDA%\Scripts;%PATH%

@REM Checking Administrator Privilege

@REM If in appveyor, skip download and installation.
IF "%APPVEYOR%"=="True" goto NoAdmin_CI

@REM This is to check if Administrator privileges are enabled.
NET SESSION > NUL 2>&1
IF %ERRORLEVEL% EQU 0 (
    ECHO [INFO] You are Administrator and able to run this script.
) ELSE (
    ECHO [FAIL] You are NOT Administrator. Please rerun with Administrator privilege.
    PING 127.0.0.1 > NUL 2>&1
    EXIT /B 1
)

:NoAdmin_CI
IF "%APPVEYOR%"=="True" (
    ECHO [INFO] Skipping checking of Administrator privilege in CI
)


@REM Checking Java
ECHO [INFO] Checking Java

@REM If in appveyor, skip download and installation.
IF "%APPVEYOR%"=="True" goto Java_CI

FOR /f %%j IN ("java.exe") DO (
    SET JAVA_HOME=%%~dp$PATH:j
)

IF %JAVA_HOME%.==. (
    ECHO [INFO] Downloading Java JDK 8u131.
    thirdParty\curl -o thirdParty\jdk.exe -L -O -H "Cookie:oraclelicense=accept-securebackup-cookie" -k "http://download.oracle.com/otn-pub/java/jdk/8u131-b11/d54c1d3a095b4ff2b6607d096fa80163/jdk-8u131-windows-i586.exe"
    ECHO [INFO] Installing Java JDK 8u131.
    thirdParty\jdk.exe /s
    del thirdParty\jdk.exe
) ELSE (
    ECHO [INFO] Java JDK exists in the environment.
    ECHO JAVA_HOME = %JAVA_HOME%
)

:Java_CI
IF "%APPVEYOR%"=="True" (
    ECHO [INFO] Skipping checking of Java in CI
)


::::::::::::::::::::
::  Installation  ::
::::::::::::::::::::

@REM Installing Microsoft VC++ for Python 2.7
IF EXIST thirdParty\VCForPython27.msi (
    ECHO [INFO] Found cached VCForPython27.msi
) ELSE (
    ECHO [INFO] Downloading VCForPython27.msi
    thirdParty\curl -o thirdParty\VCForPython27.msi -kLO https://download.microsoft.com/download/7/9/6/796EF2E4-801B-4FC4-AB28-B59FBF6D907B/VCForPython27.msi
    ECHO [INFO] Installing VCForPython27.msi
    msiexec /i thirdParty\VCForPython27.msi /qn /quiet /norestart
)

@REM Checking and Installing 7zip
ECHO [INFO] Checking 7zip

@REM If in appveyor, skip download and installation.
IF "%APPVEYOR%"=="True" goto 7zip_CI

@REM Trying to download and install 7zip
where 7z.exe >nul 2>&1
IF %ERRORLEVEL% EQU 0 (
    ECHO [INFO] You already have 7Zip in windows system.
) ELSE (
    IF EXIST thirdParty\7z1604.exe (
        ECHO [INFO] Found cached 7z1604.exe
    ) ELSE (
        ECHO [INFO] Downloading 7Zip.
        thirdParty\curl -o thirdParty\7z1604.exe -kLO http://www.7-zip.org/a/7z1604.exe
    )
    ECHO [INFO] Installing 7Zip.
    thirdParty\7z1604.exe /S
)

IF EXIST "C:\Program Files\7-Zip\" (
    mklink /d "C:\7-Zip\" "C:\Program Files\7-Zip\"
) ELSE (
    mklink /d "C:\7-Zip\" "C:\Program Files (x86)\7-Zip\"
)
SETX PATH "C:\7-Zip\;%PATH%" /m
SET "PATH=C:\7-Zip\;%PATH%"

:7zip_CI
IF "%APPVEYOR%"=="True" (
    ECHO [INFO] Skipping checking of 7zip in CI
    SET "PATH=C:\7-Zip\;%PATH%"
)

@REM fetching gechodriver 0.14
IF EXIST thirdParty\geckodriver\geckodriver.exe (
    ECHO [INFO] Found cached geckodriver
) ELSE (
    ECHO [INFO] Downloading geckodriver-v0.14.0-win32.zip
    thirdParty\curl -o thirdParty\geckodriver.zip -kLO  https://github.com/mozilla/geckodriver/releases/download/v0.14.0/geckodriver-v0.14.0-win32.zip
    7z x thirdParty\geckodriver.zip
    mkdir thirdParty\geckodriver
    move /Y thirdParty\geckodriver.exe thirdParty\geckodriver
    del thirdParty\geckodriver.zip
)


@REM Installing ffmpeg
IF NOT EXIST "%CD%"\ffmpeg\bin\ffmpeg.exe (
    ECHO [INFO] Downloading FFMPEG ...
    thirdParty\curl -o thirdParty\ffmpeg.7z -kLO "https://github.com/ypwalter/ffmpeg/blob/master/ffmpeg-20160527-git-d970f7b-win32-static.7z?raw=true"
    ECHO [INFO] Installing FFMPEG ...
    7z x "thirdParty\ffmpeg.7z"
    move /Y ffmpeg-20160527-git-d970f7b-win32-static ffmpeg
    del thirdParty\ffmpeg.7z
    ECHO [INFO] FFMPEG is installed.
) ELSE (
    ECHO [INFO] FFMPEG had been installed.
)


mklink /d "C:\FFMPEG\" "%CD%\ffmpeg\bin\"
IF NOT "%APPVEYOR%"=="True" (
    SETX PATH "C:\FFMPEG\;%PATH%" /m
)
SET PATH=C:\FFMPEG\;%PATH%


@REM Installing Sikuli

IF EXIST thirdParty\sikulixsetup.jar (
    ECHO [INFO] Found cached sikulixsetup.jar
) ELSE (
    ECHO [INFO] Downloading SikuliX 1.1.0
    thirdParty\curl -o thirdParty\sikulixsetup.jar -kLO https://launchpad.net/sikuli/sikulix/1.1.0/+download/sikulixsetup-1.1.0.jar
)

ECHO [INFO] Installing SikuliX 1.1.0
IF NOT "%APPVEYOR%"=="True" (
    "C:\Program Files\Java\jdk1.8.0_131\bin\java" -jar thirdParty\sikulixsetup.jar options 1.1 2
) ELSE (
    java -jar thirdParty\sikulixsetup.jar options 1.1 2
)
copy scripts\runsikuli* thirdParty\
@echo on


@REM Installing OBS

IF "%APPVEYOR%"=="True" GOTO SkipConda

IF NOT EXIST "C:\Program Files (x86)\obs-studio\bin\32bit\obs32.exe" (
    ECHO [INFO] Downloading OBS ...
    pushd thirdParty
    del OBS-Studio-18.0.1-Full.zip
    curl -kLO "https://github.com/jp9000/obs-studio/releases/download/18.0.1/OBS-Studio-18.0.1-Full.zip"
    ECHO [INFO] Installing OBS ...
    7z x OBS-Studio-18.0.1-Full.zip -o"C:\Program Files (x86)\obs-studio"
    popd
    SET FIRST_OBS=True
    ECHO [INFO] OBS is installed.
) ELSE (
    ECHO [INFO] OBS had been installed.
)


@REM Installing Miniconda

where conda.exe >nul 2>&1
IF %ERRORLEVEL% EQU 0 (
    ECHO [INFO] You already have conda in windows system.
) ELSE (
    ECHO [INFO] Downloading Miniconda.
    thirdParty\curl -o thirdParty\conda2.exe -kLO "https://repo.continuum.io/miniconda/Miniconda2-latest-Windows-x86.exe"
    ECHO [INFO] Installing Miniconda.
    thirdParty\conda2.exe /InstallationType=JustMe /RegisterPython=0 /S /D=C:\Miniconda2\
    SETX PATH "C:\Miniconda2\;C:\Miniconda2\Scripts\;%PATH%" /m
    SET "PATH=C:\Miniconda2\Scripts\;C:\Miniconda2\;%PATH%"
    del thirdParty\conda2.exe
)

:SkipConda
IF "%APPVEYOR%"=="True" (
    ECHO [INFO] Skipping checking of conda in CI
    ECHO [INFO] Skipping OBS in CI
)

@REM Configuring Miniconda and Virtualenv
conda config --set always_yes yes --set changeps1 no
conda install psutil
ECHO [INFO] Creating Miniconda virtualenv (It might take some time to finish.)
conda create -q -n env-python python=2.7 numpy scipy nose pywin32 pip matplotlib==1.5.3 runipy==0.1.5


::::::::::::::::::::
::    Browsers    ::
::::::::::::::::::::

@REM If in appveyor, skip download and installation
IF NOT "%APPVEYOR%"=="True" (
    @REM Installing firefox
    ECHO [INFO] Downloading Firefox.
    thirdParty\curl -kLO https://ftp.mozilla.org/pub/firefox/releases/49.0.1/win32/en-US/Firefox%%20Setup%%2049.0.1.exe
    ECHO [INFO] Installing Firefox.
    "Firefox%%20Setup%%2049.0.1.exe" -ms -ma

    @REM Installing chrome
    ECHO [INFO] Downloading Chrome.
    thirdParty\curl -kLO http://dl.google.com/chrome/install/googlechromestandaloneenterprise.msi
    ECHO [INFO] Installing Chrome.
    msiexec /i "googlechromestandaloneenterprise.msi" /qn /quiet /norestart

    del Firefox%%20Setup%%2049.0.1.exe
    del googlechromestandaloneenterprise.msi
)

IF EXIST "C:\Program Files\Mozilla Firefox\" (
    mklink /d "C:\Firefox\" "C:\Program Files\Mozilla Firefox\"
) ELSE (
    mklink /d "C:\Firefox\" "C:\Program Files (x86)\Mozilla Firefox\"
)
SETX PATH "C:\Firefox\;%PATH%" /m
SET "PATH=C:\Firefox\;%PATH%"

IF EXIST "C:\Program Files\Google\Chrome\Application\" (
    mklink /d "C:\Chrome\" "C:\Program Files\Google\Chrome\Application\"
) ELSE (
    mklink /d "C:\Chrome\" "C:\Program Files (x86)\Google\Chrome\Application\"
)
SETX PATH "C:\Chrome\;%PATH%" /m
SET "PATH=C:\Chrome\;%PATH%"

::::::::::::::::::::
::  Hasal  Setup  ::
::::::::::::::::::::

IF "%APPVEYOR%"=="True" (
    ECHO [INFO] Setup in virtualenv
    activate env-python
    pip install pywin32-ctypes==0.0.1
    pip install coverage mitmproxy
    pip install thirdParty\opencv_python-2.4.13-cp27-cp27m-win32.whl
    python setup.py install
) ELSE (
    @REM Installing mitmproxy & opencv2 & Hasal
    activate env-python & pip install pywin32-ctypes==0.0.1 mitmproxy thirdParty\opencv_python-2.4.13-cp27-cp27m-win32.whl & certutil -p "" thirdParty\mitmproxy-ca-cert.p12 & python setup.py install & python scripts\cv2_checker.py
)


:::::::::::::::::::::::::
::  User Interactions  ::
:::::::::::::::::::::::::

IF "%APPVEYOR%"=="True" GOTO SkipUserInteractions


@REM OBS License Agreement
IF "%FIRST_OBS%"=="True" (
    IF EXIST "C:\Program Files (x86)\obs-studio\bin\32bit\obs32.exe" (
        pushd "C:\Program Files (x86)\obs-studio\bin\32bit\"
        ECHO [INFO] Launching OBS for License Agreement.
        ECHO.
        ECHO "[INFO] If there is error message about missing MSVCP120.dll,"
        ECHO "[INFO] please install Visual C++ Redistributable Packages, vcredist_x86.exe and vcredist_x64.exe, for 64 bits system"
        ECHO "[INFO] from https://support.microsoft.com/zh-tw/help/3179560/update-for-visual-c-2013-and-visual-c-redistributable-package ."
        ECHO "[INFO] For 32 bits system, only vcredist_x86.exe is required."
        ECHO [INFO] ** Please CLOSE OBS after accepting License Agreement **
        obs32.exe
        popd
    ) ELSE (
        ECHO [WARN] Can not find OBS binary file.
    )
)

:SkipUserInteractions
IF "%APPVEYOR%"=="True" (
    ECHO [INFO] Skipping SkipUser Interactions
)


::::::::::::::::::::
::    Finished    ::
::::::::::::::::::::
echo "Please download certificates for Hasal from google drive or ask whoever know about it."
@REM Bootstrap done
