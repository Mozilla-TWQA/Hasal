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
    ECHO [INFO] Downloading Java JDK 7u79.
    thirdParty\curl -L -O -H "Cookie:oraclelicense=accept-securebackup-cookie" -k "http://download.oracle.com/otn-pub/java/jdk/7u79-b15/jdk-7u79-windows-i586.exe"
    ECHO [INFO] Installing Java JDK 7u79.
    jdk-7u79-windows-i586.exe /s
    del jdk-7u79-windows-i586.exe
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
IF EXIST VCForPython27.msi (
    ECHO [INFO] Found cached VCForPython27.msi
) ELSE (
    ECHO [INFO] Downloading VCForPython27.msi
    thirdParty\curl -kLO https://download.microsoft.com/download/7/9/6/796EF2E4-801B-4FC4-AB28-B59FBF6D907B/VCForPython27.msi
    ECHO [INFO] Installing VCForPython27.msi
    msiexec /i VCForPython27.msi /qn /quiet /norestart
    del VCForPython27.msi
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
    IF EXIST 7z1604.exe (
        ECHO [INFO] Found cached 7z1604.exe
    ) ELSE (
        ECHO [INFO] Downloading 7Zip.
        thirdParty\curl -kLO http://www.7-zip.org/a/7z1604.exe
        ECHO [INFO] Installing 7Zip.
        7z1604.exe /S
        SETX PATH "C:\Program Files\7-Zip;C:\Program Files (x86)\7-Zip;%PATH%" /m
        SET "PATH=C:\Program Files\7-Zip;C:\Program Files (x86)\7-Zip;%PATH%"
        del 7z1604.exe
    )
)

:7zip_CI
IF "%APPVEYOR%"=="True" (
    ECHO [INFO] Skipping checking of 7zip in CI
    SET "PATH=C:\Program Files\7-Zip;%PATH%"
)

@REM fetching gechodriver 0.14
IF EXIST geckodriver-v0.14.0-win32.zip (
    ECHO [INFO] Found cached geckodriver-v0.14.0-win32.zip
) ELSE (
    ECHO [INFO] Downloading geckodriver-v0.14.0-win32.zip
    thirdParty\curl -kLO  https://github.com/mozilla/geckodriver/releases/download/v0.14.0/geckodriver-v0.14.0-win32.zip
    7z x geckodriver-v0.14.0-win32.zip
    mkdir thirdParty\geckodriver
    move /Y geckodriver.exe thirdParty\geckodriver
)

IF NOT "%APPVEYOR%"=="True" (
    del geckodriver-v0.14.0-win32.zip
)


@REM Installing ffmpeg
IF NOT EXIST "%CD%"\ffmpeg\bin\ffmpeg.exe (
    ECHO [INFO] Downloading FFMPEG ...
    pushd thirdParty
    curl -kLO "https://github.com/ypwalter/ffmpeg/blob/master/ffmpeg-20160527-git-d970f7b-win32-static.7z?raw=true"
    popd
    ECHO [INFO] Installing FFMPEG ...
    7z x "thirdParty\ffmpeg-20160527-git-d970f7b-win32-static.7z_raw=true"
    move /Y ffmpeg-20160527-git-d970f7b-win32-static ffmpeg
    del "thirdParty\ffmpeg-20160527-git-d970f7b-win32-static.7z_raw=true"
    ECHO [INFO] FFMPEG is installed.
) ELSE (
    ECHO [INFO] FFMPEG had been installed.
)

IF NOT "%APPVEYOR%"=="True" (
    SETX PATH "%CD%\ffmpeg\bin\;%PATH%" /m
)
SET PATH=%CD%\ffmpeg\bin\;%PATH%


@REM Installing Sikuli

IF EXIST sikulixsetup-1.1.0.jar (
    ECHO [INFO] Found cached sikulixsetup-1.1.0.jar
) ELSE (
    ECHO [INFO] Downloading SikuliX 1.1.0
    thirdParty\curl -kLO https://launchpad.net/sikuli/sikulix/1.1.0/+download/sikulixsetup-1.1.0.jar
)
ECHO [INFO] Installing SikuliX 1.1.0
java -jar sikulixsetup-1.1.0.jar options 1.1 2
copy runsikuli* thirdParty\
copy sikuli*.jar thirdParty\
copy scripts\runsikuli* thirdParty\
del runsikuli*
del sikuli*.jar
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
    thirdParty\curl -kLO "https://repo.continuum.io/miniconda/Miniconda2-latest-Windows-x86.exe"
    ECHO [INFO] Installing Miniconda.
    Miniconda2-latest-Windows-x86.exe /InstallationType=JustMe /RegisterPython=0 /S /D=C:\Miniconda2\
    SETX PATH "C:\Miniconda2\;C:\Miniconda2\Scripts\;%PATH%" /m
    SET "PATH=C:\Miniconda2\Scripts\;C:\Miniconda2\;%PATH%"
    del Miniconda2-latest-Windows-x86.exe
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

SETX PATH "C:\Program Files\Mozilla Firefox;C:\Program Files (x86)\Mozilla Firefox;%PATH%" /m
SET "PATH=C:\Program Files\Mozilla Firefox;C:\Program Files (x86)\Mozilla Firefox;%PATH%"
SETX PATH "C:\Program Files\Google\Chrome\Application\;C:\Program Files (x86)\Google\Chrome\Application\;%PATH%" /m
SET "PATH=C:\Program Files\Google\Chrome\Application\;C:\Program Files (x86)\Google\Chrome\Application\;%PATH%"

::::::::::::::::::::
::  Hasal  Setup  ::
::::::::::::::::::::

IF "%APPVEYOR%"=="True" (
    ECHO [INFO] Setup in virtualenv
    activate env-python
    pip install coverage mitmproxy
    pip install thirdParty\opencv_python-2.4.13-cp27-cp27m-win32.whl
    python setup.py install
) ELSE (
    @REM Installing mitmproxy & opencv2 & Hasal
    activate env-python & pip install mitmproxy thirdParty\opencv_python-2.4.13-cp27-cp27m-win32.whl & certutil -p "" thirdParty\mitmproxy-ca-cert.p12 & python setup.py install & python scripts\cv2_checker.py
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
        ECHO "[INFO] please install Visual C++ Redistributable Packages from https://www.microsoft.com/en-us/download/details.aspx?id=40784"
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
