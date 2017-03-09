#!/bin/bash
# Author: askeing
# Version: 0.0.1


LOG_FILE="bootstrap.log"

func_log_exec () {
    # It will only log the STDOUT result, and the return code will always be 0.
    $@ >> ${LOG_FILE}
}

func_log () {
    echo "$@" | tee -a ${LOG_FILE}
}

################
# Prerequisite #
################

RET_SUCCESS="0"

func_log "[START] `date +%Y-%m-%d:%H:%M:%S`"

# OS Platform
PLATFORM=`uname`
if [[ ${PLATFORM} == 'Linux' ]]; then
    func_log "[INFO] Your platform is Linux."
elif [[ ${PLATFORM} == 'Darwin' ]]; then
    func_log "[FAIL] Your platform is Mac OS X, not Linux."
    exit 1
else
    func_log "[FAIL] Your platform is $PLATFORM not Linux."
    exit 1
fi

# Checking requirements
func_install_requirement () {
    echo "[EXEC] $@"
    $@
    if [[ ${RET_SUCCESS} != `echo $?` ]]; then
        func_log "[FAIL] Install failed."
        return 1
    fi
}

declare -a REQUIREMENTS=(
    "java"
    )
declare -a REQUIREMENTS_INSTALL=(
    "sudo apt-get install -y --force-yes default-jre"
    )

REQUIREMENTS_LENGTH=${#REQUIREMENTS[@]}

for (( i=1; i<${REQUIREMENTS_LENGTH}+1; i++ ));
do
    func_log "${i}/${REQUIREMENTS_LENGTH}: Check ${REQUIREMENTS[${i}-1]} ..."
    if [[ ${RET_SUCCESS} != `which ${REQUIREMENTS[${i}-1]} > /dev/null; echo $?` ]]; then
        func_log "[FAIL] No ${REQUIREMENTS[${i}-1]} installed."
        func_install_requirement ${REQUIREMENTS_INSTALL[${i}-1]}
        INSTALL_RET=$?
        if [[ ${RET_SUCCESS} != ${INSTALL_RET} ]]; then
            func_log "[FAIL] Install ${REQUIREMENTS[${i}-1]} failed."
        else
            func_log "[INFO] Install ${REQUIREMENTS[${i}-1]} done."
        fi
    fi
done
func_log "[PASS] Checking finished."

################
# Installation #
################

# https://launchpad.net/~mc3man/+archive/ubuntu/trusty-media
func_log "[INFO] Add mc3man/trusty-media for ffmpeg ..."
sudo add-apt-repository --yes ppa:mc3man/trusty-media

func_log "[INFO] Running apt-get update ..."
sudo apt-get -yq update

func_log "[INFO] Install Requirements ..."

# tools
func_log "[INFO] Installing tools ..."
sudo apt-get install -y --force-yes unzip wget git

# python
func_log "[INFO] Installing python ..."
# python-pip has some problem of urllib3
# ref: http://stackoverflow.com/questions/27341064/how-do-i-fix-importerror-cannot-import-name-incompleteread
sudo apt-get install -y --force-yes python-dev python-virtualenv
sudo easy_install pip

# build toolchain
func_log "[INFO] Installing build toolchain ..."
sudo apt-get install -y build-essential cmake libffi-dev libssl-dev

# req of numpy, scipy
func_log "[INFO] Installing req of numpy, scipy ..."
sudo apt-get install -y --force-yes libblas-dev liblapack-dev libatlas-base-dev libyaml-dev gfortran

# OpenCV
func_log "[INFO] Installing OpenCV ..."
sudo apt-get install -y --force-yes libopencv-dev python-opencv

# ffmpeg
func_log "[INFO] Installing ffmpeg ..."
sudo apt-get install -y --force-yes ffmpeg

# avconv
func_log "[INFO] Installing avconv ..."
sudo apt-get install -y --force-yes libav-tools

# imagemagick, for Speed Index
func_log "[INFO] Installing imagemagick ..."
sudo apt-get install -y --force-yes imagemagick

# mitmproxy
func_log "[INFO] Installing mitmproxy ..."
sudo apt-get install -y --force-yes mitmproxy

# sikulix
func_log "[INFO] Installing Sikulix 1.1.0 ..."
sudo apt-get install -y --force-yes libcv2.4 libcvaux2.4 libhighgui2.4 libtesseract-dev wmctrl xdotool
rm -rf thirdParty/sikulixsetup-1.1.0.jar
wget -P thirdParty/ https://launchpad.net/sikuli/sikulix/1.1.0/+download/sikulixsetup-1.1.0.jar
java -jar thirdParty/sikulixsetup-1.1.0.jar options 1.1

# geckodriver
wget --output-document=./thirdParty/geckodriver-v0.14.0.tar.gz https://github.com/mozilla/geckodriver/releases/download/v0.14.0/geckodriver-v0.14.0-linux64.tar.gz
mkdir -p ./thirdParty/geckodriver/
tar -xvzf ./thirdParty/geckodriver-v0.14.0.tar.gz -C ./thirdParty/geckodriver/
chmod a+x ./thirdParty/geckodriver/geckodriver



func_log "[INFO] Install Requirements finished."

echo ""

###############
# Hasal Setup #
###############

func_log "[INFO] Creating virtualenv ..."
virtualenv .env-python
source .env-python/bin/activate

func_log "[INFO] Linking opencv's cv2.so to virtualenv ..."
CV2_SO_PATH=`find /usr/ -name "cv2.so" -print | head -n 1`  # only get first result
ln -s ${CV2_SO_PATH} .env-python/lib/python2.7/site-packages/cv2.so

func_log "[INFO] Upgrading pip itself ..."
pip install -U pip
pip install -U setuptools

func_log "[INFO] Install numpy and scipy ..."
pip install requests[security] numpy scipy

func_log "[INFO] Python Setup Install ..."
pip install -r requirements.txt
python setup.py install

############
# Checking #
############

echo ""

func_log "[INFO] Checking Python CV2 Module ..."
func_log_exec ./scripts/cv2_checker.py
./scripts/cv2_checker.py
CHECK_CV2_RET=$?

func_log "[INFO] Checking System Packages ..."
func_log_exec ./scripts/sys_pkg_checker.py
./scripts/sys_pkg_checker.py
CHECK_SYS_RET=$?

echo ""

###########
# Browser #
###########

if [[ ${TRAVIS} ]]; then
    func_log "[WARN] Skip checking browsers."
else
    func_log "[INFO] Disable the Unity Web App Integration Prompt."
    gsettings set com.canonical.unity.webapps integration-allowed false

    func_log "[INFO] Checking browsers ..."

    which firefox > /dev/null
    CHK_FX_RET=$?
    if [[ ${RET_SUCCESS} == ${CHK_FX_RET} ]]; then
        func_log "[INFO] Your Firefox version: `firefox -v`"
    else
        func_log "[INFO] Installing \"Firefox\" ..."
        sudo apt-get install firefox
    fi

    which google-chrome > /dev/null
    CHK_GC_RET=$?
    if [[ ${RET_SUCCESS} == ${CHK_GC_RET} ]]; then
        func_log "[INFO] Your Chrome version: `google-chrome --version`"
    else
        func_log "[INFO] Installing \"Chrome\" ..."
        wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
        sudo sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
        sudo apt-get update
        sudo apt-get install google-chrome-stable
    fi
fi

########
# Done #
########

func_log "[INFO] Done."
func_log "[END] `date +%Y-%m-%d:%H:%M:%S`"

if [[ ${RET_SUCCESS} == ${CHECK_CV2_RET} ]] && [[ ${RET_SUCCESS} == ${CHECK_SYS_RET} ]]; then
    func_log "### Hasal ##############"
    func_log "# Welcome to Hasal! :) #"
    func_log "########################"

    if [[ ${TRAVIS} ]]; then
        func_log "[NOTE] Skip download Certificates into Hasal's folder ..."
    else
        func_log "[NOTE] Please login your Mozilla account, and download Certificates into Hasal's folder ..."
        firefox --new-window http://goo.gl/ALcw0B &
    fi
    func_log ""

else
    func_log "### Hasal ########################"
    func_log "# It seems like something wrong! #"
    func_log "# Please check bootstrap log.    #"
    func_log "##################################"
    func_log ""
    exit 1
fi
