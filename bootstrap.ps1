function Add-EnvPath {
    param(
        [Parameter(Mandatory=$true)]
        [string] $Path,

        [ValidateSet('Machine', 'User', 'Session')]
        [string] $Container = 'Session'
    )

    if ($Container -ne 'Session') {
        $containerMapping = @{
            Machine = [EnvironmentVariableTarget]::Machine
            User = [EnvironmentVariableTarget]::User
        }
        $containerType = $containerMapping[$Container]

        $persistedPaths = [Environment]::GetEnvironmentVariable('Path', $containerType) -split ';'
        if ($persistedPaths -notcontains $Path) {
            $persistedPaths = $persistedPaths + $Path | where { $_ }
            [Environment]::SetEnvironmentVariable('Path', $persistedPaths -join ';', $containerType)
        }
    }

    $envPaths = $env:Path -split ';'
    if ($envPaths -notcontains $Path) {
        $envPaths = $envPaths + $Path | where { $_ }
        $env:Path = $envPaths -join ';'
    }
}

########################
#                      #
#  Install Chocolatey  #
#                      #
########################

# installation of Chocolatey package management
"[INFO] Installing Chocolatey"
If ($PSVersionTable.PSVersion.Major -Match "2") {
    iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))
} Else {
    iwr https://chocolatey.org/install.ps1 -UseBasicParsing | iex
}
choco feature enable -n=allowGlobalConfirmation

########################
#                      #
#  Hasal Installation  #
#                      #
########################

# installation of tools
$tmp = & CMD /C curl --help >$null 2>&1
If ($lastexitcode -notmatch 0) {
    "[INFO] Installing Curl"
    choco install curl
    If ($lastexitcode -notmatch 0) {
        "[ERROR] There were problems when installing curl."
        Exit
    }
} Else {
    "[INFO] Curl found in current system. Not going to install it."
}

$tmp = & CMD /C git --help >$null 2>&1
If ($lastexitcode -notmatch 0) {
    "[INFO] Installing git"
    choco install git.install
    If ($lastexitcode -notmatch 0) {
        "[ERROR] There were problems when installing git."
        Exit
    }
    SETX PATH "C:\Program Files\Git\bin;$env:Path" /m
    Add-EnvPath "C:\Program Files\Git\bin;"
} Else {
    "[INFO] Git found in current system. Not going to install it."
}

# installation of Hasal prerequisite
$tmp = & CMD /C java -version >$null 2>&1
If ($lastexitcode -notmatch 0) {
    "[INFO] Installing Java 8 -version 8.0.121"
    choco install jre8
    If ($lastexitcode -notmatch 0) {
        "[ERROR] There were problems when installing jre8."
        Exit
    }
    SETX PATH "C:\Program Files\Java\jre1.8.0_121\bin;$env:Path" /m
    Add-EnvPath "C:\Program Files\Java\jre1.8.0_121\bin;"
} Else {
    "[INFO] Java found in current system. Not going to install it."
}


$tmp = & CMD /C ffmpeg -help >$null 2>&1
If ($lastexitcode -notmatch 0) {
    "[INFO] Installing FFMPEG"
    choco install ffmpeg -version 3.2.2.20161219
    If ($lastexitcode -notmatch 0) {
        "[ERROR] There were problems when installing ffmpeg."
        Exit
    }
    SETX PATH "C:\ProgramData\chocolatey\lib\ffmpeg\tools\ffmpeg-3.2.2-win32-static\bin\;$env:Path" /m
    Add-EnvPath "C:\ProgramData\chocolatey\lib\ffmpeg\tools\ffmpeg-3.2.2-win32-static\bin\;"
} Else {
    "[INFO] FFMPEG found in current system. Not going to install it."
}

$tmp = & CMD /C conda -help >$null 2>&1
If ($lastexitcode -notmatch 0) {
    "[INFO] Installing MiniConda"
    choco install miniconda
    If ($lastexitcode -notmatch 0) {
        "[ERROR] There were problems when installing miniconda."
        Exit
    }
    SETX PATH "C:\Program Files\Miniconda2\Scripts\;C:\Program Files\Miniconda2\;$env:Path" /m
    Add-EnvPath "C:\Program Files\Miniconda2\Scripts\;C:\Program Files\Miniconda2\;"
} Else {
    "[INFO] MiniConda found in current system. Not going to install it."
}

"[INFO] Downloading VCForPython27.msi"
CMD /C curl -kLO https://download.microsoft.com/download/7/9/6/796EF2E4-801B-4FC4-AB28-B59FBF6D907B/VCForPython27.msi
"[INFO] Installing VCForPython27.msi"
msiexec /i VCForPython27.msi /qn /quiet /norestart
If ($lastexitcode -notmatch 0) {
    "[ERROR] There were problems when installing VCForPython27.msi"
    Exit
}
"[INFO] Removing VCForPython27.msi"
Remove-Item VCForPython27.msi

# installation of browsers
"[INFO] Installing Chrome"
choco install googlechrome
If ($lastexitcode -notmatch 0) {
    "[ERROR] There were problems when installing Chrome"
    Exit
}
SETX PATH "C:\Program Files\Google\Chrome\Application\;C:\Program Files (x86)\Google\Chrome\Application\;$env:Path" /m
Add-EnvPath "C:\Program Files\Google\Chrome\Application\;"
Add-EnvPath "C:\Program Files (x86)\Google\Chrome\Application\;"

"[INFO] Installing Firefox"
choco install firefox -y
If ($lastexitcode -notmatch 0) {
    "[ERROR] There were problems when installing Firefox"
    Exit
}
SETX PATH "C:\Program Files\Mozilla Firefox;C:\Program Files (x86)\Mozilla Firefox;$env:Path" /m
Add-EnvPath "C:\Program Files\Mozilla Firefox;"
Add-EnvPath "C:\Program Files (x86)\Mozilla Firefox;"

# installation of sikuli
"[INFO] Installing SikuliX 1.1.0"
choco install sikulix
If ($lastexitcode -notmatch 0) {
    "[ERROR] There were problems when installing SikuliX"
    Exit
}

########################
#                      #
#     Hasal Setup      #
#                      #
########################

"[INFO] Creating Miniconda virtualenv (It might take some time to finish.)"
conda config --set always_yes yes --set changeps1 no
conda install psutil
conda create -q -n env-python python=2.7 numpy scipy nose pywin32 pip matplotlib==1.5.3 runipy==0.1.5

Copy-Item C:\ProgramData\chocolatey\lib\sikulix\content\* .\thirdParty\
Copy-Item .\scripts\runsikuli* .\thirdParty\

If (Test-Path C:\Miniconda2\) {
    CMD /C "C:\Miniconda2\envs\env-python\Scripts\pip" install mitmproxy
    CMD /C "C:\Miniconda2\envs\env-python\Scripts\pip" install thirdParty\opencv_python-2.4.13-cp27-cp27m-win32.whl
    CMD /C "C:\Miniconda2\envs\env-python\Scripts\pip" install thirdParty\opencv_python-2.4.13.2-cp27-cp27m-win_amd64.whl
    CMD /C certutil -p "" thirdParty\mitmproxy-ca-cert.p12
    CMD /C "C:\Miniconda2\envs\env-python\python" setup.py install
    CMD /C "C:\Miniconda2\envs\env-python\python" scripts\cv2_checker.py
} Else {
    CMD /C "C:\Program Files\Miniconda2\envs\env-python\Scripts\pip" install mitmproxy
    CMD /C "C:\Program Files\Miniconda2\envs\env-python\Scripts\pip" install thirdParty\opencv_python-2.4.13-cp27-cp27m-win32.whl
    CMD /C "C:\Program Files\Miniconda2\envs\env-python\Scripts\pip" install thirdParty\opencv_python-2.4.13.2-cp27-cp27m-win_amd64.whl
    CMD /C certutil -p "" thirdParty\mitmproxy-ca-cert.p12
    CMD /C "C:\Program Files\Miniconda2\envs\env-python\python" setup.py install
    CMD /C "C:\Program Files\Miniconda2\envs\env-python\python" scripts\cv2_checker.py
}
