#!/bin/bash
# Author: askeing
# Version: 0.0.1

func_log () {
    echo "$@" | tee -a bootstrap-mac.log
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
    "brew"
    "python"
    "pip"
    "virtualenv")
declare -a REQUIREMENTS_INSTALL=(
    '/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"'
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
    fi
done
func_log "[PASS] Checking finished."


################
# Installation #
################

func_log "[INFO] Creating virtualenv ..."
virtualenv .env-python
source .env-python/bin/activate

func_log "[INFO] Upgrading pip itself ..."
pip install -U pip

func_log "[INFO] Running brew install homebrew/science ..."
# updating brew before tap homebrew/science
brew update
brew tap homebrew/science
brew update

func_log "[INFO] Running brew install ffmpeg ..."
brew install ffmpeg --with-fdk-aac --with-ffplay --with-freetype --with-frei0r --with-libass --with-libvo-aacenc --with-libvorbis --with-libvpx --with-opencore-amr --with-openjpeg --with-opus --with-rtmpdump --with-schroedinger --with-speex --with-theora --with-tools

func_log "[INFO] Running brew install libav ..."
brew install libav

func_log "[INFO] Running brew install opencv ..."
brew install homebrew/science/opencv

func_log "[INFO] Linking opencv's cv2.so to virtualenv ..."
CV2_SO_PATH=`find /usr/local/Cellar/opencv/ -name "cv2.so"`
ln -s ${CV2_SO_PATH} .env-python/lib/python2.7/site-packages/cv2.so

func_log "[INFO] Python Setup Install ..."
pip install -r requirements.txt
python setup.py install

func_log "[INFO] Checking Python CV2 Module ..."
PYTHON_CV2_CHECK_RESULT=`./scripts/cv2_checker.py`
func_log ${PYTHON_CV2_CHECK_RESULT}
BOOTSTRAP_RET=$?

func_log "[INFO] Done."
func_log "[END] `date +%Y-%m-%d:%H:%M:%S`"
func_log ""

if [[ ${RET_SUCCESS} == ${BOOTSTRAP_RET} ]]; then
    echo "### Hasal ##############"
    echo "# Welcome to Hasal! :) #"
    echo "########################"
else
    echo "### Hasal ########################"
    echo "# It seems like something wrong! #"
    echo "# Please check bootstrap log.    #"
    echo "##################################"
fi

# Return cv2_checker's return code as bootstrap return code.
exit ${BOOTSTRAP_RET}
