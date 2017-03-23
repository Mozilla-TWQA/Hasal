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
if [[ ${PLATFORM} == 'Darwin' ]]; then
    func_log "[INFO] Your platform is Mac OS X."
elif [[ ${PLATFORM} == 'Linux' ]]; then
    func_log "[FAIL] Your platform is Linux, not Mac OS X."
    exit 1
else
    func_log "[FAIL] Your platform is $PLATFORM not Mac OS X."
    exit 1
fi

# Checking Homebrew first
func_log "[INFO] Checking Homebrew ..."
which brew || (func_log "[INFO] Installing Homebrew ..."; /usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)")
which brew || (func_log "[FAIL] Installing Homebrew failed."; exit 1)
func_log "[Info] Checking Homebrew passed."

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
    "python"
    "pip"
    "virtualenv")
declare -a REQUIREMENTS_INSTALL=(
    "brew install python"
    "sudo easy_install pip"
    "sudo pip install virtualenv")

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

func_log "[INFO] Installing Requirements ..."
func_log "[INFO] Running brew install homebrew/science ..."
# updating brew before tap homebrew/science
brew update
brew tap homebrew/science
brew tap caskroom/cask
brew update

# tools
brew install wget

# ffmpeg, skip on CI
# OpenCV
if [[ ${TRAVIS} ]]; then
    func_log "[WARN] Skip installing ffmpeg on Travis CI, due to it is very slow!"
    func_log "[INFO] Installing opencv without ffmpeg (on Travis CI) ..."
    brew install homebrew/science/opencv || brew link --overwrite homebrew/python/numpy
else
    func_log "[INFO] Installing ffmpeg ..."
    brew install ffmpeg --with-fdk-aac --with-ffplay --with-freetype --with-frei0r --with-libass --with-libvo-aacenc --with-libvorbis --with-libvpx --with-opencore-amr --with-openjpeg --with-opus --with-rtmpdump --with-schroedinger --with-speex --with-theora --with-tools
    func_log "[INFO] Installing opencv with ffmpeg ..."
    brew install homebrew/science/opencv --with-ffmpeg -v
fi

# libav (avconv)
func_log "[INFO] Installing libav ..."
brew install libav

# imagemagick, for Speed Index
func_log "[INFO] Installing imagemagick ..."
brew install imagemagick

# mitmproxy
func_log "[INFO] Installing mitmproxy ..."
brew install mitmproxy

# sikulix
func_log "[INFO] Installing Sikulix 1.1.0 ..."
rm -rf thirdParty/sikulixsetup-1.1.0.jar
wget -P thirdParty/ https://launchpad.net/sikuli/sikulix/1.1.0/+download/sikulixsetup-1.1.0.jar
brew cask install java
java -jar thirdParty/sikulixsetup-1.1.0.jar options 1.1

# geckodriver
func_log "[INFO] Installing geckodriver ..."
wget --output-document=./thirdParty/geckodriver-v0.14.0.tar.gz https://github.com/mozilla/geckodriver/releases/download/v0.14.0/geckodriver-v0.14.0-macos.tar.gz
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

func_log "[INFO] Upgrading pip itself ..."
pip install -U pip

func_log "[INFO] Linking opencv's cv2.so to virtualenv ..."
CV2_SO_PATH=`find /usr/local/Cellar/opencv/ -name "cv2.so" | tail -1`
ln -s ${CV2_SO_PATH} .env-python/lib/python2.7/site-packages/cv2.so

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

###########
# Browser #
###########

if [[ ${TRAVIS} ]]; then
    func_log "[WARN] Skip checking browsers."
else
    func_log "[INFO] Checking browsers ..."

    ls /Applications/Firefox.app/Contents/MacOS/firefox > /dev/null
    CHK_FX_RET=$?
    if [[ ${RET_SUCCESS} == ${CHK_FX_RET} ]]; then
        func_log "[INFO] Your Firefox version: `/Applications/Firefox.app/Contents/MacOS/firefox -v`"
    else
        func_log "[INFO] Installing \"Firefox\" ..."
        brew cask install firefox
    fi

    ls "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" > /dev/null
    CHK_GC_RET=$?
    if [[ ${RET_SUCCESS} == ${CHK_GC_RET} ]]; then
        func_log "[INFO] Your Chrome version: `/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --version`"
    else
        func_log "[INFO] Installing \"Chrome\" ..."
        brew cask install google-chrome
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
        open -a firefox -g http://goo.gl/ALcw0B
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
